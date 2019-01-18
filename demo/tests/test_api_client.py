from unittest import TestCase
from django_unifi_portal.unifi_client import UnifiClient


def get_unifi_client():
    return UnifiClient()

class TestAPI(TestCase):

    def test_can_instantiate_instance_of_unificlient(self):
        print("test_can_instantiate_instance_of_unificlient")
        ufc = get_unifi_client()
        assert isinstance(ufc, UnifiClient)

    def test_login_as_admin(self):
        print("test_login_as_admin")
        ufc = get_unifi_client()
        status_code = ufc.login_on_unifi_server()
        assert status_code == 200

    def test_authorize_guest(self):
        print("test_authorize_guest")
        ufc = get_unifi_client()
        ufc.login_on_unifi_server()
        status_code = ufc.authorize_guest(guest_mac='04:4b:ed:25:c6:b3',
                                          minutes='10',
                                          ap_mac='04:4b:ed:25:c6:b3')

        assert status_code == 200

    def test_unauthorize_guest(self):
        print("test_unauthorize_guest")
        ufc = get_unifi_client()
        ufc.login_on_unifi_server()
        status_code = ufc.unauthorize_guest(guest_mac='04:4b:ed:25:c6:b3')

        assert status_code == 200

    def test_logout_admin(self):
        print("test_logout_admin")
        ufc = get_unifi_client()
        ufc.login_on_unifi_server()
        status_code = ufc.logout_from_unifi_server()
        assert status_code == 200

    def test_send_authorization(self):
        print("test_send_authorization")
        ufc = get_unifi_client()
        ufc.login_on_unifi_server()
        status_code = ufc.send_authorization(guest_mac='04:4b:ed:25:c6:b3',
                                             minutes='10',
                                             ap_mac='04:4b:ed:25:c6:b3')
        assert status_code == 200
