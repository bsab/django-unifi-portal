#!/usr/bin/env python
# coding: utf-8
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy

from forms import UnifiRegistrationForm
from models import UnifiUser


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
