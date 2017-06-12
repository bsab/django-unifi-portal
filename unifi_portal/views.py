#!/usr/bin/env python
# coding: utf-8
import logging

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import PermissionRequiredMixin

from forms import UnifiRegistrationForm
from models import UnifiUser
from unifi_client import UnifiClient

from django.shortcuts import redirect
@login_required
def myredirect(request):
    print "view::myredirect"
    _url = request.GET.get('url', '')
    print _url
    return redirect(_url)

class PermissionView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(PermissionView, self).get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PermissionView, self).dispatch(request, *args, **kwargs)


class UnifiUserRegistration(FormView):
    template_name = 'registration.html'
    form_class = UnifiRegistrationForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super(UnifiUserRegistration, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        return self.render_to_response(context)

    def authorize_as_unifi_guest(self, user):
        print "*********authorize_as_unifi_guest*********"
        unifi_client=None
        try:
            self._mac = self.request.GET.get('id', '')
            self._ap = self.request.GET.get('ap', '')
            self._url = self.request.GET.get('url', '')
            self._t = self.request.GET.get('t', '')

            print "mac:", self._mac
            print "ap:", self._ap
            print "t:", self._t
            print "url:", self._url

            unifi_client = UnifiClient()
            self._t = 5;  # ATTENZIONE!!!
            unifi_client.send_authorization(self._mac, self._ap, self._t)

            permission = Permission.objects.get(name='Can Navigate')
            user.user_permissions.add(permission)

        except Exception as exp:
            print "Exception::validate_unifi_request" + str(exp)
            pass;
        return unifi_client

    def form_valid(self, form):
        print "*********form_valid*********"
        user = form.save(commit=False);
        user.set_password(form.cleaned_data['password']);
        user.username = form.cleaned_data['username'].lower();
        user.email = form.cleaned_data['username'].lower();   #ATTENZIONE: maschero la username con la email
        user.is_active = True;
        user.save();

        unifi_user = UnifiUser();
        unifi_user.user = user;
        unifi_user.save();

        #setto il permesso ad utilizzare la wifi
        self.authorize_as_unifi_guest(user)

        # execute login
        user_logged = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']);
        login(self.request, user_logged);

        return HttpResponseRedirect(self.get_success_url())
