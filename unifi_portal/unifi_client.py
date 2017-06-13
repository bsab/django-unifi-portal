import json
import requests
import logging
import cookielib
import ssl
import time
from requests_toolbelt import SSLAdapter

from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiClient(object):
    """
        Constructor takes the Unifi credentials and base URL to set up a UnifiClient
    """
    def __init__(self, port=8443, version='v4', site_id='default'):
        """Create a UnifiClient object.

        Arguments:
            port     -- the port of the unifi server
            version  -- the base version of the API [v2|v3|v4]
            site_id  -- the site ID to connect to (UniFi >= 3.x)

        """

        self.version = port
        self.version = version
        self.site_id = site_id
        self.__unifiUser = settings.UNIFI_USER
        self.__unifiPass = settings.UNIFI_PASSWORD
        self.__unifiServer = settings.UNIFI_SERVER

        self.__cookie_file = "/tmp/unifi_cookie"

        # Use a Session object to handle cookies.
        self.__session = requests.Session()
        cj = cookielib.LWPCookieJar(self.__cookie_file)

        # Load existing cookies (file might not yet exist)
        try:
            cj.load()
        except:
            pass
        self.__session.cookies = cj

        # Use an SSLAdapter to work around SSL handshake issues.
        self.__session.mount(self.get_resource_url(), SSLAdapter(ssl.PROTOCOL_SSLv23))

        pass

    def get_resource_url(self, path_name=None):
        """T ake path_name parameter and return a valid formatted URL for a unifi resource"""
        if path_name:
            # Return a URL for a specific resource
            url = str.format('{0}{1}:{2}/{3}', 'https://', self.__unifiServer, '8443', path_name)
            logger.debug('URL: {0}'.format(url))
            return url
        else:
            url = str.format('{0}{1}:{2}/', 'https://', self.__unifiServer, '8443')
            return url;

    def _login_as_admin(self):
        """ Log into the API as Admin """
        data = {
            'username': self.__unifiUser,
            'password': self.__unifiPass
        }

        login_version = 'login'
        if self.version == 'v4' or self.version == 'v5':
            login_version = 'api/login'

        login_url = self.get_resource_url(login_version)
        login_response = self.__session.post(login_url, data=json.dumps(data), verify=False)

        print "********** login_response **********"
        print login_response.text
        print "************************************"

        return login_response.status_code

    def authorize_guest(self,  guest_mac, ap_mac, minutes):
        """
            Authorize a guest based on his MAC address.
            Arguments:
                guest_mac     -- the guest MAC address : aa:bb:cc:dd:ee:ff
                ap_mac        -- access point MAC address (UniFi >= 3.x) (optional)
                minutes       -- duration of the authorization in minutes
        """

        auth = {
            'cmd': 'authorize-guest',
            'mac': guest_mac,
            'minutes': minutes,
        }

        if self.version == 'v3' or self.version == 'v4' or self.version == 'v5':
            api_version = 'api/s/' + self.site_id + '/'

        api_url = self.get_resource_url('api/s/default/cmd/stamgr')
        auth_response = self.__session.post(api_url, data=json.dumps(auth))
        print "********** auth_response **********"
        print auth_response.status_code
        print auth_response.text
        print "************************************"

        return auth_response.status_code

    def _logout_admin(self):
        """ Log out from the API. """
        logout_url = self.get_resource_url('logout')
        logout_response = self.__session.get(logout_url, timeout=5)
        print "********** logout_response **********"
        print logout_response.status_code
        print logout_response.text
        print "************************************"

        return logout_response.status_code

    def send_authorization(self, guest_mac, ap_mac, minutes):
        """ Login on Unifi Server and authorize a guest based on his MAC address"""
        self._login_as_admin();

        res = self.authorize_guest(guest_mac=guest_mac,
                                   minutes=minutes,
                                   ap_mac=ap_mac)
        return res


def _authorize_unifi_guest(request):
    """ Authorize a guest based on parameters passed through the request. """
    _mac = request.GET.get('id', '')
    _ap = request.GET.get('ap', '')
    _url = request.GET.get('url', '')
    # _t = request.GET.get('t', '')
    _t = settings.UNIFI_TIMEOUT_MINUTES

    ctx = {
        'guest_mac': _mac,
        'ap_mac': _ap,
        'minutes': _t,
        'url': _url,
        'last_login': time.strftime("%c")
    }
    unifi_client = UnifiClient()
    unifi_client.send_authorization(_mac, _ap, _t)

    return ctx
