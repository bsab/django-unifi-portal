from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.views import generic, static
from django.contrib.auth import views as auth_views

from unifi_portal import forms
from unifi_portal.views import index_view, UnifiUserRegistration


urlpatterns = [

    url(r'guest/s/default/$', index_view, name='index'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html',
        'authentication_form': forms.SocialLoginForm},
        name='unifi_social_login'),
    url(r'^logout/$', auth_views.logout, name='logout'),

    url(r'^unifi-portal/registration/$', UnifiUserRegistration.as_view(), name="unifi_registration"),
    #url(r'', include(frontend_urls)),
]
