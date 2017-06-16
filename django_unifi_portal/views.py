#!/usr/bin/env python
# coding: utf-8

import time
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.utils.http import is_safe_url
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings

from unifi_client import UnifiClient
from django_unifi_portal import forms
from django_unifi_portal.models import UnifiUser

class UserAuthorizeView(SingleObjectMixin, TemplateView):
    """ Authorize a guest based on parameters passed through the request. """

    template_name = 'index.html'

    def get_user_profile_inst(self):
        up = None;
        u = User.objects.get(username=self.request.user)
        try:
            up = UnifiUser.objects.get(user=u)
        except:
            up = None;
        return up;

    def get_context_data(self, **kwargs):
        """Update view context."""
        #context = super(UserAuthorizeView, self).get_context_data(**kwargs)
        context={}

        try:
            _mac = self.request.GET.get('id', '')
            _ap = self.request.GET.get('ap', '')
            _url = self.request.GET.get('url', '')
            # _t = self.request.GET.get('t', '')
            _t = settings.UNIFI_TIMEOUT_MINUTES
            _last_login = time.strftime("%c")

            context.update({
                'guest_mac': _mac,
                'ap_mac': _ap,
                'minutes': _t,
                'url': _url,
                'last_login': _last_login
            })
            print "context->", context

            # Saving info on userprofile Model
            userprofile = self.get_user_profile_inst()
            if userprofile:
                userprofile.guest_mac = _mac
                userprofile.last_backend_login = _last_login
                userprofile.save()

            # Ask authorization to unifi server
            unifi_client = UnifiClient()
            unifi_client.send_authorization(_mac, _ap, _t)

            #if _url:
            #    return HttpResponseRedirect(_url)
        except Exception as exp_debug:
            print "EXCEPTION: " + str(exp_debug)
            pass

        return context

    def post(self, request, *args, **kwargs):
        """Deny post requests."""
        return HttpResponseForbidden();

    def get(self, request, *args, **kwargs):
        """Response with rendered html template."""
        context = self.get_context_data()

        if '_url' in context:
            if context['_url']: #if i try to go on an url without wifi login
                return HttpResponseRedirect(context['_url'])

        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserAuthorizeView, self).dispatch(request, *args, **kwargs)


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

        # Set the request url from unifi into a cookie to get in registration form
        try:
            request.session['mynext'] = self.request.GET['next']
        except Exception as e:
            print "EXCEPTION:UnifiUserLogin " + str(e)
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
    """ Provides users the ability to logout.  """
    url = '/unifi-portal/login/'
    template_name = 'logged_out.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(UnifiUserLogout, self).get(request, *args, **kwargs)


class UnifiUserRegistration(FormView):
    template_name = 'registration.html'
    form_class = forms.UnifiRegistrationForm

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
        user.first_name = form.cleaned_data['first_name'].lower();
        user.last_name = form.cleaned_data['last_name'].lower();
        user.is_active = True;
        user.save();

        unifi_user = UnifiUser();
        unifi_user.user = user;
        unifi_user.phone = form.cleaned_data['phone'];
        unifi_user.gender = form.cleaned_data['gender'];
        unifi_user.save();

        # execute login
        user_logged = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']);
        login(self.request, user_logged);

        return HttpResponseRedirect(self.get_success_url())
