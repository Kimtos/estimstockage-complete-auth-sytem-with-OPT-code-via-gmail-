"""pydrive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('get_entry', views.get_entry, name='home'),
    path('verify', views.verify, name='verify'),
    path('validate_otp', views.validate_otp, name='validate_otp'),
    path('dashboard', views.dashboard, name='dashboard'),

    path('save_folder', views.save_folder, name='save_folder'),

    path('forgot_password',views.forgot_password, name='forgot_password'),
    path('change_psw', views.change_psw, name='change_psw'),

    path('settings', views.settings, name='profile'),
    path('logout', views.logout, name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
