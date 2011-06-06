#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *
from controller.forms import *

import datetime,json

from django.utils.encoding import smart_unicode

def signin(request):
    t = loader.get_template('signin.html')
    context = RequestContext(request)
    context['next_url'] = '/'
    if request.GET.get('next',False):
        context['next_url'] = request.GET['next']
    
    if request.user.is_authenticated():
        context['message'] = 'You are already logined'
        return HttpResponse(t.render(context))
      
    if request.method != 'POST':
        return HttpResponse(t.render(context))
        
    if not (request.POST.get('username',False) and request.POST.get('password',False) ):
        context['message'] = 'Field is missing'
        return HttpResponse(t.render(context))
        
    username = request.POST['username']
    password = request.POST['password']
    
    user = authenticate(username=username,password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            if request.POST['next']:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect('/')
        else:
            return HttpResponse(user.username+' is not active. Please check email and click activation link')
    else:
        context['message'] = 'Sign in Failed'
        return HttpResponse(t.render(context))
    

def signout(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/signin/')
    
    userane=request.user.username
    logout(request)
    t = loader.get_template('signin.html')
    context = RequestContext(request)
    context['message'] = 'Successfully logout'
    return HttpResponse(t.render(context))

import re
def signup(request):
    if request.user.is_authenticated():
        return HttpResponse('You are already logined.')
    
    if not request.POST:
        t = loader.get_template('register.html')
        context = RequestContext(request)
        context['form']=RegisterForm()
        return HttpResponse(t.render(context))
    
    form = RegisterForm(request.POST)
    if form.is_valid():
        username=form.cleaned_data['username']
        email=form.cleaned_data['email']
        password=form.cleaned_data['password1']
        
        #parameter validation
        username_valid= re.match('[\w0-9]*',username) and len(username) >= 3 and len(username) < 16
        
        password_valid=True
        #password_valid=len(password) >= 6 
        email_valid=re.match('[\w.]*@\w*\.[\w.]*',email)
        
        if not (username_valid and password_valid and email_valid):
            return HttpResponse(' invalid input ' )
        #TODO : VALID CHECK
        try:
            user = User.objects.get(username=username)
            return HttpResponse(username+' is already taken')
        except:
            new_user = User.objects.create_user(username,email,password)
            new_user.is_active = False
            new_user.save()
            
            shaSource= username + email
            activation_key=encode(shaSource)
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
    
            new_profile = UserProfile(user=new_user, activation_key=activation_key, key_expires=key_expires)
            new_profile.save()
            
            email_subject = smart_unicode('Cloud31 계정 인증을 완료해 주세요!', encoding='utf-8', strings_only=False, errors='strict')
            email_body = 'http://localhost:8000/confirm/?key='+activation_key
    
            send_mail(email_subject, email_body, 'Cloud31<cloud31.email@gmail.com>',[email])
            
            return HttpResponse(username + ' Registered. Check Mail' )
    else:
        return HttpResponse('Error Occured.')


from django.shortcuts import get_object_or_404

def confirm(request):
    if request.user.is_authenticated():
        return HttpResponse('You are already logined.')
    
    activation_key=request.GET['key']
        
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires < datetime.datetime.today():
        return HttpResponse('Expired Key. ')
    
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    return HttpResponse(user_account.username + ' is Activated. ')
    

from hashlib import sha1
def encode(string) : 
  return sha1(string).hexdigest()
    