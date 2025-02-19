import os
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from datetime import date
import shutil
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from app.models import user, verification,  folder
import smtplib
import zipfile
import hashlib
from django.core.files.storage import default_storage


def home(request):
    if request.session and request.session.__contains__('user_id'):
        return redirect('dashboard')
    return render(request, 'index.html')


def dashboard(request):
    if 'user_id' in request.session.keys() and request.session['user_id'] is not None:
        if request.GET and request.GET.__contains__('starred'):
            return render(request, 'dashboard.html', {'starred': True})
        if request.GET and request.GET.__contains__('folder_id'):
            return render(request, 'dashboard.html', {'folder_id': request.GET['folder_id']})
        return render(request, 'dashboard.html')
    return redirect('index')


def get_entry(request):
    page_name = 'index'
    if request.POST and request.POST['submit'] == 'Login':
        page_name = login(request)
    else:
        page_name = signup(request)
    return redirect(page_name)


def test(req):
    return render(req, 'test.html')


def login(request):
    # check if verified
    # maintain session

    if request.POST is not None and request.POST['email'] is not None and request.POST['password'] is not None:
        try:
            tempuser = user.objects.get(user_email=request.POST['email'])
        except user.DoesNotExist:
            tempuser = None

        if tempuser is None:
            messages.error(request, message="User not exists!")
            return 'index'
        else:
            password = request.POST['password']
            hashed = hashlib.md5(password.encode())
            password = hashed.hexdigest()
            if str(password) == str(tempuser.user_password):
                try:
                    verified = verification.objects.get(user_id=tempuser.id)
                except verification.DoesNotExist:
                    verified = None

                if verified is None:
                    request.session['user_id'] = tempuser.id
                    request.session['user_email'] = tempuser.user_email
                    return 'dashboard'
                else:
                    return 'verify'
            else:
                messages.error(request, message="Wrong password!")
                return 'index'
    else:
        return 'index'


def logout(request):
    del request.session['user_id']
    del request.session['user_email']
    return redirect('index')


def signup(request):
    # send verification.(records in user table and verification table)
    print("SIGNUP")
    if request.POST is not None and request.POST['email'] is not None and request.POST['password'] is not None:
        mail = request.POST['email']
        password = request.POST['password']

        try:
            tempuser = user.objects.get(user_email=mail)
        except user.DoesNotExist:
            tempuser = None

        if tempuser is not None:
            messages.error(request, message="L'utilisateur exist déjà!")
            return 'index'

        hashed = hashlib.md5(password.encode())
        password = hashed.hexdigest()

        tempuser = user(user_email=mail, user_password=password)
        tempuser.save()
        otp = random.randint(100000, 999999)
        verificationRecord = verification(user_id=tempuser.id, otp=otp)
        verificationRecord.save()
        send_email(mail, "OTP", 'Here is your one time verification code:<h4>' + str(otp) + "</h4>")
        return 'verify'
    return 'index'


def verify(request):
    return render(request, 'verify.html')


def validate_otp(request):
    tempuser = user.objects.get(user_email=request.POST['email_field'])
    verified = verification.objects.get(user_id=tempuser.id)
    if verified is not None:
        if int(verified.otp) == int(request.POST['otp_field']):
            verified.delete()
            request.session['user_id'] = tempuser.id
            request.session['user_email'] = tempuser.user_email
            os.mkdir('user_data/' + str(tempuser.id))
            return redirect('dashboard')
        else:
            return render(request, 'verify.html')
    else:
        return redirect('index')


def save_folder(request):
    print(request.POST)
    if request.session and request.session.__contains__('user_id') and request.session['user_id'] == int(
            request.POST['user_id']):
        if len(request.POST['parent_id']) == 0:
            parentId = None
            link = 'user_data/' + request.POST['user_id'] + '/' + request.POST['folder_name']
            os.mkdir(link)
        else:
            parentId = request.POST['parent_id']
            parent = folder.objects.get(id=parentId)
            link = parent.folder_link + "/" + request.POST['folder_name']
            os.mkdir(link)

        folder(folder_name=request.POST['folder_name'],
               folder_link=str(link),
               folder_date=date.today(),
               folder_starred=False,
               parent_id=parentId,
               user_id=int(request.POST['user_id'])
               ).save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


def change_psw(request):
    if request.session and request.session.__contains__('user_id') and request.POST:
        obj = user.objects.get(id=int(request.session['user_id']))
        if obj:
            if request.POST.__contains__('acc_psw') and request.POST['acc_psw']:
                hashed = hashlib.md5(request.POST['acc_psw'].encode())
                password = hashed.hexdigest()
                obj.user_password = password
                obj.save()
                return redirect('profile')
            if request.POST.__contains__('vault_psw') and request.POST['vault_psw']:
                hashed = hashlib.md5(request.POST['vault_psw'].encode())
                password = hashed.hexdigest()
                obj.user_vault_psw = password
                obj.save()
                return redirect('profile')

    return redirect('profile')


def settings(req):
    return render(req, 'profile.html')


def forgot_password(request):
    if user.objects.filter(user_email=request.POST['email']).count() > 0:
        temp_psw = str(random.randint(10000000, 99999999))
        hashed = hashlib.md5(temp_psw.encode())
        password = hashed.hexdigest()
        userObj = user.objects.get(user_email=request.POST['email'])
        userObj.user_password = password
        userObj.save()
        send_email(request.POST['email'], "Reset Password",
                   "<b>Your new temporary password is:" + temp_psw + "</b><h4>It is highly recommended to change your password from user profile :)</h4>")
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})


def send_email(mail, subject, temp_message):
    message = MIMEMultipart("Drive")
    message['subject'] = subject
    message['From'] = 'gracekimbouala@gmail.com'
    message['To'] = mail
    message.attach(MIMEText(temp_message, 'html'))

    try:
        mail_server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        print(mail_server.__dict__)
        mail_server.starttls()
        mail_server.login(user="gracekimbouala@gmail.com", password="siyu ooxt hwis njwu")
        mail_server.sendmail("gracekimbouala@gmail.com", mail, msg=message.as_string())
        mail_server.quit()
    except Exception as E:
        print(E)
