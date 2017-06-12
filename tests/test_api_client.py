from unittest import TestCase
from unifi_portal.views import UnifiClient


def get_unifi_client():
    return UnifiClient()

class TestAPI(TestCase):

    def test_can_instantiate_instance_of_unificlient(self):
        ufc = get_unifi_client();
        assert isinstance(ufc, UnifiClient)

    def test__login_as_admin(self):
        ufc = get_unifi_client();
        status_code = ufc._login_as_admin()
        assert status_code == 200

    def test_authorize_guest(self):
        ufc = get_unifi_client();
        ufc._login_as_admin()
        status_code = ufc.authorize_guest(guest_mac='04:4b:ed:25:c6:b3',
                                          minutes='10',
                                          ap_mac='04:4b:ed:25:c6:b3')

        assert status_code == 200

    def test__logout_admin(self):
        ufc = get_unifi_client();
        ufc._login_as_admin()
        status_code = ufc._logout_admin()
        assert status_code == 200

    def test_send_authorization(self):
        ufc = get_unifi_client();
        status_code = ufc.send_authorization(guest_mac='04:4b:ed:25:c6:b3',
                                             minutes='10',
                                             ap_mac='04:4b:ed:25:c6:b3')
        assert status_code == 200
