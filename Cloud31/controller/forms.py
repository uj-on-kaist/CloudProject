#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.core import validators
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _


class RegisterForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={ 'placeholder': 'ID' }),
                                label=_(u'username'))
    real_name = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={ 'placeholder': '이름' }),
                                label=_(u'name'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict({ 'placeholder': '이메일 주소' },
                                                               maxlength=75)),
                             label=_(u'email address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': '비밀번호' }, render_value=False),
                                label=_(u'password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={ 'placeholder': '비밀번호 확인' }, render_value=False),
                                label=_(u'password')+u' 확인')
    dept = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={ 'placeholder': '부서' }),
                                label=_(u'dept'))
    position = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs={ 'placeholder': '직급' }),
                                label=_(u'position'))