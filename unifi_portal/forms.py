from django import forms
from django.forms import ModelForm
from django.template import Template
from django.contrib.auth.forms import User
from django.contrib.auth.forms import AuthenticationForm

from material import Layout, Row, Column, Fieldset, Span2, Span3, Span5, Span6, Span10
from . import form_mixin as forms

class UnifiLoginForm(AuthenticationForm):
    #ATTENZIONE: maschero la username con la email
    username = forms.EmailField(label="Email Address", required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    template = Template("""
    {% form %}
        {% part form.username prefix %}<i class="material-icons prefix">email</i>{% endpart %}
        {% part form.password prefix %}<i class="material-icons prefix">lock</i>{% endpart %}
    {% endform %}
    """)

    logo = Template("""
        <p style="text-align:center"> <img src="/static/img/logo.png">  </p>
        <br>
    """)

    social_buttons = Template("""
        <p style="text-align:center"><a href="/auth/login/facebook" class="waves-effect waves-light btn-large blue"><i class="fa fa-facebook" aria-hidden="true"></i> Sign in with facebook</a></p>
        <br>
    """)

    buttons = Template("""
        <a href="{% url 'unifi_registration' %}" class="waves-effect waves-teal btn-flat">Register</a>
        <button class="waves-effect waves-light btn" type="submit">Login</button>
    """)


    title = "Unifi Login"

class UnifiRegistrationForm(ModelForm):
    username = forms.EmailField(label="Email Address")
    #email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=((None, ''), ('F', 'Female'), ('M', 'Male'), ('O', 'Other')))
    receive_news = forms.BooleanField(required=False, label='I want to receive news and special offers')
    agree_toc = forms.BooleanField(required=True, label='I agree with the Terms and Conditions')

    layout = Layout('username',
                    Row('password', 'password_confirm'),
                    Fieldset('Personal details',
                             Row('first_name', 'last_name'),
                             'gender', 'receive_news', 'agree_toc'))

    template = Template("""
    {% form %}
        {% part form.username prefix %}<i class="material-icons prefix">email</i>{% endpart %}
        {% part form.password prefix %}<i class="material-icons prefix">lock_open</i>{% endpart %}
        {% part form.password_confirm prefix %}<i class="material-icons prefix">lock_open</i>{% endpart %}
    {% endform %}
    """)

    buttons = Template("""
        <button class="waves-effect waves-light btn" type="submit">Submit</button>
    """)

    title = "Registration form"

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
