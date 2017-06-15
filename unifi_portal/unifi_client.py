import json
import requests
import logging
import cookielib
import ssl
from requests_toolbelt import SSLAdapter

from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiClient(object):
    """
        Constructor takes the Unifi credentials and base URL to set up a UnifiClient
    """
    def __init__(self):
        """ Create a UnifiClient object. """

        self.version = settings.UNIFI_VERSION
        self.site_id = settings.UNIFI_SITE_ID
        self.__unifiUser = settings.UNIFI_USER
        self.__unifiPass = settings.UNIFI_PASSWORD
        self.__unifiServer = settings.UNIFI_SERVER
        self.__unifiPort = settings.UNIFI_PORT

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
        self.__session.mount(self._get_resource_url(), SSLAdapter(ssl.PROTOCOL_SSLv23))

        pass

    def _get_resource_url(self, path_name=None):
        """ Take path_name parameter and return a valid formatted URL for a unifi resource. """
        if path_name:
            # Return a URL for a specific resource
            url = str.format('{0}{1}:{2}/{3}', 'https://', self.__unifiServer, '8443', path_name)
            logger.debug('URL: {0}'.format(url))
            return url
        else:
            url = str.format('{0}{1}:{2}/', 'https://', self.__unifiServer, '8443')
            return url;

    def _is_authorized(self, guest_mac):
        """Return true if the guest is already authorized."""

        if self.version == 'v3' or self.version == 'v4' or self.version == 'v5':
            api_version = 'api/s/' + self.site_id + '/'

        api_url = self._get_resource_url(api_version + 'stat/sta')
        clients_response = self.__session.post(api_url)
        client_list=json.loads(clients_response.text)['data']

        #Find the client who hat this mac address
        try:
            client_found = next(client for client in client_list if client["mac"] == guest_mac)
            return (client_found['authorized'] == 'True')
        except:
            return False

    def login_on_unifi_server(self):
        """ Log into the API unifi server """
        data = {
            'username': self.__unifiUser,
            'password': self.__unifiPass
        }

        login_version = 'login'
        if self.version == 'v4' or self.version == 'v5':
            login_version = 'api/login'

        login_url = self._get_resource_url(login_version)
        login_response = self.__session.post(login_url, data=json.dumps(data), verify=False)
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

        api_url = self._get_resource_url(api_version + 'cmd/stamgr')
        auth_response = self.__session.post(api_url, data=json.dumps(auth))
        return auth_response.status_code

    def unauthorize_guest(self,  guest_mac):
        """
            Unauthorize  a guest based on his MAC address.
            Arguments:
                guest_mac     -- the guest MAC address : aa:bb:cc:dd:ee:ff
        """

        unauth = {
            'cmd': 'unauthorize-guest',
            'mac': guest_mac,
        }

        if self.version == 'v3' or self.version == 'v4' or self.version == 'v5':
            api_version = 'api/s/' + self.site_id + '/'

        api_url = self._get_resource_url('api/s/default/cmd/stamgr')
        auth_response = self.__session.post(api_url, data=json.dumps(unauth))
        return auth_response.status_code

    def logout_from_unifi_server(self):
        """ Log out from the API. """
        logout_url = self._get_resource_url('logout')
        logout_response = self.__session.get(logout_url, timeout=5)
        return logout_response.status_code

    def send_authorization(self, guest_mac, ap_mac, minutes):
        """ Login on Unifi Server and authorize a guest based on his MAC address"""
        self.login_on_unifi_server();

        status_code = -1;
        if not self._is_authorized(guest_mac):
            status_code = self.authorize_guest(guest_mac=guest_mac,
                                               minutes=minutes,
                                               ap_mac=ap_mac)
            return status_code
