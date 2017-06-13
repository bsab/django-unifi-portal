from django.conf.urls import include, url
from unifi_portal.views import UnifiUserLogin, UnifiUserLogout, UnifiUserRegistration, authorize_unifi_guest


urlpatterns = [

    url(r'guest/s/default/$', authorize_unifi_guest, name='index'),

    url(r'^unifi-portal/login/$', UnifiUserLogin.as_view(), name='unifi_login'),

    url(r'^unifi-portal/logout/$',UnifiUserLogout.as_view(), name='unifi_logout'),

    url(r'^unifi-portal/registration/$', UnifiUserRegistration.as_view(), name="unifi_registration"),

]
