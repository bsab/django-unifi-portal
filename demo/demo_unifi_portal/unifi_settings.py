#################################################
#        UNIFI SETTINGS CONFIGURATION           #
#################################################

from django.core.urlresolvers import reverse_lazy

UNIFI_INSTALLED_APPS = [
    # material apps
    'material',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'django_unifi_portal',
]

UNIFI_LOGIN_URL = '/unifi-portal/login'
UNIFI_LOGIN_REDIRECT_URL = reverse_lazy('index')

UNIFI_TEMPLATE_CONTEXT_PROCESSORS = [
        'material.frontend.context_processors.modules',
        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
        'unifi_portal.context_processor.unifi_context'
]

UNIFI_TEMPLATE_BUILTINS = 'material.templatetags.material_form'

UNIFI_AUTHENTICATION_BACKENDS = (

    # Others auth providers (e.g. Google, OpenId, etc)

    # Facebook OAuth2
    'social_core.backends.facebook.FacebookAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',

    # Django
    'django.contrib.auth.backends.ModelBackend',

)

UNIFI_SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'django_unifi_portal.pipeline.manage_auth_already_associated',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'django_unifi_portal.pipeline.require_email',
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.debug.debug',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'django_unifi_portal.pipeline.user_details',
    'django_unifi_portal.pipeline.save_profile',
    'social_core.pipeline.debug.debug',
)

# Define SOCIAL_AUTH_FACEBOOK_SCOPE to get extra permissions from facebook.
# Email is not sent by default, to get it, you must request the email permission:
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, about, email, birthday, gender, hometown, languages'
}

UNIFI_SERVER = "<your UniFi Server ip>
UNIFI_PORT = <your Unifi Server Port>  # default is 8443
UNIFI_VERSION = 'v4'
UNIFI_SITE_ID = 'default'

# It's important to note that if this server is offsite, you need to have port 8443 forwarded through to it
UNIFI_SSID = '<your ssid name>'
UNIFI_LOGO = '<relative path under the static folder to the logo png>'

UNIFI_USER = "<your UniFi Username>"
UNIFI_PASSWORD = "<your UniFi Password>"
UNIFI_TIMEOUT_MINUTES = <minutes>  # ex. 8 hours is 480

# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = "<your Facebook key>"
SOCIAL_AUTH_FACEBOOK_SECRET = "<your Facebook api secret>"

