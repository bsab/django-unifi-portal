import unittest

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.db import IntegrityError

from django.conf import settings
from django_unifi_portal.models import UnifiUser

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        try:

            try:
                self.user = User.objects.get(username='lennon@thebeatles.com')
            except User.DoesNotExist:
                self.user = User()
                self.user.set_password('johnpassword')
                self.user.username = 'lennon@thebeatles.com'
                self.user.email = 'lennon@thebeatles.com'
                self.user.is_active = True
                self.user.save()

            fbuserprofile = UnifiUser()
            fbuserprofile.user = self.user
            fbuserprofile.save()
        except Exception as exp:
            print("EXCEPTION:LoginTestCase-->", str(exp))
            pass


    def testIndexView(self):
        print(">> testIndexView")
        self.setUp()
        self.client.login(username='lennon@thebeatles.com', password='johnpassword')

        test_url_ihone = '/guest/s/default/?id=04:4b:ed:25:c6:b3&ap=f0:9f:c2:39:86:f2&t=1496998102&url=http://captive.apple.com%2fhotspot-detect.html&ssid=ClubLaVela'
        test_url_samsung='/guest/s/default/?id=88:ad:d2:e4:cf:f4&ap=f0:9f:c2:39:86:f2&t=1496848672&url=http://connectivitycheck.gstatic.com%2fgenerate_204&ssid=ClubLaVela'
        response = self.client.get(test_url_samsung)

        self.assertEqual(response.status_code, 200)


    def testIndexViewWrongUrl(self):
        print(">> testIndexView")
        self.setUp()
        self.client.login(username='lennon@thebeatles.com', password='johnpassword')

        test_url_ihone = '/guest/s/default/?id=04:4b:ed:25:c6:b3&ap=f0:9f:c2:39:86:f2&t=1496998102&url=http://captive.apple.com%2fhotspot-detect.html&ssid=ClubLaVela'
        test_url_samsung='/guest/?id=88:ad:d2:e4:cf:f4&ap=f0:9f:c2:39:86:f2&t=1496848672&url=http://connectivitycheck.gstatic.com%2fgenerate_204&ssid=ClubLaVela'
        response = self.client.get(test_url_samsung)

        self.assertEqual(response.status_code, 404)
