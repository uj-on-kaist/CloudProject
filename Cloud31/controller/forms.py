#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.core import validators
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _


class RegisterForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={ 'placeholder': 'username' }),
                                label=_(u'username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({ 'placeholder': 'email' },
                                                               maxlength=75)),
                             label=_(u'email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': 'password' }, render_value=False),
                                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': 'confirm' }, render_value=False),
                                label=_(u'password')+u' 확인')