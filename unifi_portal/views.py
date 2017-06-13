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
from django.utils.http import is_safe_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView

from forms import UnifiRegistrationForm
from models import UnifiUser
from unifi_client import _authorize_unifi_guest
from unifi_portal import forms

@login_required
def authorize_unifi_guest(request):
    """ Authorize a guest based on his MAC address.  """
    try:
        ctx = _authorize_unifi_guest(request)
        return render_to_response('index.html', ctx, RequestContext(request))
    except Exception as exp:
        return HttpResponseForbidden()

class UnifiUserLogin(FormView):
    """
    Provides the ability to login as a user with a username and password
    """
    template_name = 'login.html'
    success_url = reverse_lazy('index')
    form_class = forms.UnifiLoginForm
    redirect_field_name = REDIRECT_FIELD_NAME

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()
        #request.session.set_cookie('mynext', self.request.GET['next']) #deprecated!

        # Set the request url from unifi into a cookie to get in registration form
        try:
            request.session['mynext'] = self.request.GET['next']
        except:
            pass;

        return super(UnifiUserLogin, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(UnifiUserLogin, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.REQUEST.get(self.redirect_field_name)
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class UnifiUserLogout(RedirectView):
    """
    Provides users the ability to logout
    """
    url = '/login/'
    template_name = 'logged_out.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(UnifiUserLogout, self).get(request, *args, **kwargs)


class UnifiUserRegistration(FormView):
    template_name = 'registration.html'
    form_class = UnifiRegistrationForm

    def get_context_data(self, **kwargs):

        context = super(UnifiUserRegistration, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('index'))
        return self.render_to_response(context)

    def form_valid(self, form):

        # Get the request url from unifi
        try:
            self.success_url = self.request.session['mynext']
        except:
            self.success_url = reverse_lazy('index') #to test!

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

        return HttpResponseRedirect(self.get_success_url())
