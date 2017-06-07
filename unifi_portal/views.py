#!/usr/bin/env python
# coding: utf-8
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.shortcuts import render

from forms import UnifiRegistrationForm
from models import UnifiUser

def index_view(request, *args, **kwargs):
    _mac = request.GET.get('id', '')
    _ap = request.GET.get('ap', '')
    _url = request.GET.get('url', '')
    _t = request.GET.get('t', '')

    print "mac:", _mac
    print "ap:", _ap
    print "t:", _t
    print "url:", _url

    context = {
    }
    return render(request, 'index.html', context)


def send_authorization(id, ap, minutes, url):
    unifiServer = settings.UNIFI_SERVER;
    unifiUser = settings.UNIFI_USER
    unifiPass = settings.UNIFI_USER

    #
    # 1) Login to Unifi Server
    #
    '''
    //Start Curl for login
    $ch = curl_init();
    // We are posting data
    curl_setopt($ch, CURLOPT_POST, TRUE);
    // Set up cookies
    $cookie_file = "/tmp/unifi_cookie";
    curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
    curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
    // Allow Self Signed Certs
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    // Force SSL3 only
    curl_setopt($ch, CURLOPT_SSLVERSION, 3);
    // Login to the UniFi controller
    curl_setopt($ch, CURLOPT_URL, "$unifiServer/login");
    curl_setopt($ch, CURLOPT_POSTFIELDS, "login=login&username=$unifiUser&password=$unifiPass");
    curl_exec ($ch);
    curl_close ($ch);
    '''

    #
    # 2) Send user to authorize and the time allowed
    #
    data = {
        'cmd': 'authorize-guest',
        'mac': id,
        'ap': ap,
        'minutes': minutes
    }
    print "data->", data

    '''
    $ch = curl_init();
    // We are posting data
    curl_setopt($ch, CURLOPT_POST, TRUE);
    // Set up cookies
    $cookie_file = "/tmp/unifi_cookie";
    curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
    curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
    // Allow Self Signed Certs
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    // Force SSL3 only
    curl_setopt($ch, CURLOPT_SSLVERSION, 3);
    // Make the API Call
    curl_setopt($ch, CURLOPT_URL, $unifiServer.'/api/cmd/stamgr');
    curl_setopt($ch, CURLOPT_POSTFIELDS, 'json='.$data);
    curl_exec ($ch);
    curl_close ($ch);
    '''

    #
    # 3) Logout of the connection
    #
    '''
    $ch = curl_init();
    // We are posting data
    curl_setopt($ch, CURLOPT_POST, TRUE);
    // Set up cookies
    $cookie_file = "/tmp/unifi_cookie";
    curl_setopt($ch, CURLOPT_COOKIEJAR, $cookie_file);
    curl_setopt($ch, CURLOPT_COOKIEFILE, $cookie_file);
    // Allow Self Signed Certs
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    // Force SSL3 only
    curl_setopt($ch, CURLOPT_SSLVERSION, 3);
    // Make the API Call
    curl_setopt($ch, CURLOPT_URL, $unifiServer.'/logout');
    curl_exec ($ch);
    curl_close ($ch);
    echo "Login successful, I should redirect to: ".$url; // $_SESSION['url'];
    sleep(8); // Small sleep to allow controller time to authorize
    header('Location: '.$url); // $_SESSION['url']);
    '''

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
        user = form.save(commit=False);
        user.set_password(form.cleaned_data['password']);
        user.username = form.cleaned_data['username'].lower();
        user.email = form.cleaned_data['email'].lower();
        user.is_active = True;
        user.save();

        unifi_user = UnifiUser();
        unifi_user.user = user;
        unifi_user.save();

        # execute login
        user_logged = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']);
        login(self.request, user_logged);

        return HttpResponseRedirect(self.get_success_url())
