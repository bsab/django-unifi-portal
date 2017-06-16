from django.conf.urls import include, url
from django_unifi_portal.views import UserAuthorizeView, UnifiUserLogin, UnifiUserLogout, UnifiUserRegistration

urlpatterns = [
    #Oauth access
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),

    # Front-End access
    url(r'guest/s/default/$', UserAuthorizeView.as_view(), name='index'),
    url(r'^unifi-portal/login/$', UnifiUserLogin.as_view(), name='unifi_login'),
    url(r'^unifi-portal/logout/$',UnifiUserLogout.as_view(), name='unifi_logout'),
    url(r'^unifi-portal/registration/$', UnifiUserRegistration.as_view(), name="unifi_registration"),

    # Back-End access

]
