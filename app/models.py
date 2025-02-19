from django.db import models
from django.forms import fields


# Create your models here.
class user(models.Model):
    user_email = models.TextField()
    user_password = models.TextField()
    user_vault_psw = models.TextField()

    def __str__(self):
        return self.user_email


class verification(models.Model):
    user = models.ForeignKey('user', on_delete=models.CASCADE)
    otp = models.IntegerField()


class folder(models.Model):
    user = models.ForeignKey('user', on_delete=models.CASCADE)
    folder_name = models.TextField()
    folder_date = models.DateField()
    folder_starred = models.BooleanField()
    folder_link = models.TextField()
    parent = models.ForeignKey('folder', on_delete=models.CASCADE)
