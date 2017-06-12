from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.views import generic, static
from django.contrib.auth import views as auth_views

from unifi_portal import forms
from unifi_portal.views import myredirect, PermissionView, UnifiUserRegistration


urlpatterns = [

    url(r'guest/s/default/$', myredirect, name="index"),
    #url(r'guest/s/default/$', validate_unifi_request, name='index'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html',
        'authentication_form': forms.SocialLoginForm},
        name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),

    url(r'^unifi-portal/registration/$', UnifiUserRegistration.as_view(), name="unifi_registration"),
]
