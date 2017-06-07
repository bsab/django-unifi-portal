import unittest

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client

from unifi_portal.models import UnifiUser

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User();
        self.user.set_password('johnpassword');
        self.user.username = 'john';
        self.user.email = 'lennon@thebeatles.com';
        self.user.is_active = True;
        self.user.save();

        fbuserprofile = UnifiUser();
        fbuserprofile.user = self.user;
        fbuserprofile.save();

    def testLogin(self):
        print ">> testLogin"
        response = self.client.login(username='john', password='johnpassword')
        self.assertEqual(response, True)

class IndexTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def testIndexView(self):
        print ">> testIndexView"
        unifi_url = '/guest/s/default/?id=88:ad:d2:e4:cf:f4&ap=f0:9f:c2:39:86:f2&t=1496848672&url=http://connectivitycheck.gstatic.com%2fgenerate_204&ssid=ClubLaVela'
        print unifi_url
        response = self.client.get(unifi_url)
        self.assertEqual(response.status_code, 200);
