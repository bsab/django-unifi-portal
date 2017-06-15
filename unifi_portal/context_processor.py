from django.conf import settings

def unifi_context(request):
  ctx = {
      'ssid': settings.UNIFI_SSID,
      'timeout': settings.UNIFI_TIMEOUT_MINUTES
  }
  return ctx