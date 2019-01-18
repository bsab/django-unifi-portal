from django.views.generic import ListView
from django_unifi_portal.models import UnifiUser
from braces.views import AjaxResponseMixin


class ListGuestView(AjaxResponseMixin, ListView):
    context_object_name = "user_list"
    template_name = "user_list.html"

    def get_queryset(self):
        return UnifiUser.objects.all()

    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ListGuestView, self).dispatch(request, *args, **kwargs)