import urllib
import json
import requests
from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from social_core.pipeline.partial import partial

from django_unifi_portal.models import UnifiUser

@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            return redirect('require_email')  # <--SE IL SOCIAL NON FORNISCE LA MAIL LA DEVO RICHIEDERE A MANO

def user_details(strategy, details, user=None, *args, **kwargs):
    """Update user details using data from provider."""
    if user:
        if not UnifiUser.objects.filter(user=user).exists():
            print("user_details:UserProfile NOT exist, creating..")
            changed = False  # flag to track changes
            protected = ('username', 'id', 'pk', 'email') + \
                        tuple(strategy.setting('PROTECTED_USER_FIELDS', []))

            # Update user model attributes with the new data sent by the current
            # provider. Update on some attributes is disabled by default, for
            # example username and id fields. It's also possible to disable update
            # on fields defined in SOCIAL_AUTH_PROTECTED_FIELDS.
            for name, value in details.items():
                if value and hasattr(user, name):
                    # Check https://github.com/omab/python-social-auth/issues/671
                    current_value = getattr(user, name, None)
                    if not current_value or name not in protected:
                        changed |= current_value != value
                        # print("user_details::name", name)
                        value = value.replace("'", " ")[0:29];
                        # print("user_details::value", value) #FIX - crash con nomi superiori ai 30 caratteri

                        setattr(user, name, value)

            if changed:
                strategy.storage.user.changed(user)


def save_profile(backend, user, response, *args, **kwargs):
    profile = None

    if not UnifiUser.objects.filter(user=user).exists():

        if backend.name == 'facebook':
            try:
                profile = UnifiUser.objects.get(user=user);
            except UnifiUser.DoesNotExist:
                profile = UnifiUser()
                profile.user = user;
                profile.save();

            profile.gender = response.get('gender');
            profile.about = response.get('about')
            profile.city = response.get('hometown')
            profile.user.email = response.get('email')

            birthday_date = None;
            try:
                birthday = response.get('birthday')
                birthday_date = datetime.strptime(birthday, '%m/%d/%Y')
            except Exception as eb:
                pass;
            profile.dob = birthday_date

            fbuid = response.get('id')
            profile.user.username = fbuid  # la mail e' troppo grande
            profile.user.save();

            try:
                image_name = 'fb_avatar_%s.jpg' % fbuid
                image_url = 'http://graph.facebook.com/%s/picture?type=large' % fbuid
                image_stream = urllib.urlopen(image_url)

                profile.picture.save(
                    image_name,
                    ContentFile(image_stream.read()),
                )
            except Exception as e:
                pass;

            # INIT - 14-12-2016
            print("FACEBOOK:seleziono lingua")
            try:
                fb_access_token = response.get('access_token');
                fb_locale_url = "https://graph.facebook.com/v2.9/" + "/me?fields=locale,location" + "&access_token=" + fb_access_token;
                print(fb_locale_url)
                r = requests.get(fb_locale_url)

                if r.status_code == 200:
                    fb_response = json.loads(str(r.text.encode("utf-8")))
                    print("fb response :", fb_response)

                    # language
                    try:
                        print("***LANG :", fb_response.get('locale')[0:2])
                        profile.language = fb_response.get('locale')[0:2]
                    except:
                        pass;

                    # city
                    try:
                        print("***LOCATION :", fb_response.get('location'))
                        profile.city = fb_response.get('location')['name']
                    except:
                        pass;

            except Exception as e:
                print("FB Exception with locale " + str(e))
                pass;
            profile.last_backend_login = backend.name;
            profile.save();
    else:
        # in questo caso sto solo richiedendo una nuova associazione social
        print("UserProfile already exist..nothing...")

        # questo e' il caso di un utente che ha cancellato l'account
        # e' poi ritornato successivamente
        profile = UnifiUser.objects.get(user=user);
        profile.user.is_active = True;
        profile.user.save();


def manage_auth_already_associated(backend, uid, user=None, *args, **kwargs):
    """ OVERRIDED: It will logout the current user
    instead of raise an exception

    Fix to resolve AuthAlreadyAssociated Exception in Python Social Auth:
     http://stackoverflow.com/questions/13018147/authalreadyassociated-exception-in-django-social-auth
   """

    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            messages.error(backend.strategy.request, _('This account is already in use.'))
            return HttpResponseRedirect(reverse('home'))
            # msg = 'This {0} account is already in use.'.format(provider)
            # raise AuthAlreadyAssociated(backend, msg)
        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': False}

