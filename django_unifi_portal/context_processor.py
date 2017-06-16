from django_unifi_portal.unifi_settings import *

def unifi_context(request):
  ctx = {
      'logo': UNIFI_LOGO,
      'ssid': UNIFI_SSID,
      'timeout': UNIFI_TIMEOUT_MINUTES
  }
  return ctx