#!/usr/bin/env python
# coding: utf-8
import logging
import time
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect

from forms import UnifiRegistrationForm
from models import UnifiUser
from unifi_client import _authorize_unifi_guest


@login_required
def authorize_unifi_guest(request):
    """ Authorize a guest based on his MAC address.  """
    print ">>>>> validate_unifi_request >>>>> "
    try:
        ctx = _authorize_unifi_guest(request)

        return render_to_response('index.html', ctx, RequestContext(request))
    except Exception as exp:
        print "Exception::validate_unifi_request" + str(exp)
        return HttpResponseForbidden()


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

        # execute login
        user_logged = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']);
        login(self.request, user_logged);

        try:
            ctx = _authorize_unifi_guest(self.request)
        except Exception as exp:
            return HttpResponseForbidden()

        return HttpResponseRedirect(self.get_success_url())
