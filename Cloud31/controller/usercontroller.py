#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

import my_emailer
from controller.forms import *

def signin(request):
    t = loader.get_template('signin.html')
    context = RequestContext(request)
    context['next_url'] = '/'

    if request.session.get('message',False):
        context['message'] = request.session['message']
        request.session['message'] = None
        return HttpResponse(t.render(context))
    else:
        request.session['message'] = None
    
    if request.GET.get('next',False):
        context['next_url'] = request.GET['next']
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/feed')
      
    if request.method != 'POST':
        return HttpResponse(t.render(context))
        
    if not (request.POST.get('username',False) and request.POST.get('password',False) ):
        context['message'] = 'Field is missing'
        return HttpResponse(t.render(context))
    
    try:
        if request.POST['keep_signed']:
            pass
    except:
        request.session.set_expiry(0)
    
    username = request.POST['username']
    password = request.POST['password']
    
    user = authenticate(username=username,password=password)
    if user is not None:
        user_profile = UserProfile.objects.get(user=user)
        if user.is_active and not user_profile.is_deactivated:
            login(request, user)
            
            user_login = UserLoginHistory(user=user)
            user_login.save()
            
            if request.POST['next']:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect('/')
        elif not user.is_active:
            context['message'] = user.username+' is not active. First check your email and click activation link'
            return HttpResponse(t.render(context))
        elif user_profile.is_deactivated:
            context['message'] = user.username+' is deactivated. Please Contact with Administrator.'
            return HttpResponse(t.render(context))
    else:
        context['message'] = '<b>Sign in Failed.</b> Check Username and Password again.'
        return HttpResponse(t.render(context))
    

def signout(request):
    if not request.user.is_authenticated():
        request.session['message'] =  'You need to login first'
    else:
        logout(request)
        request.session['message'] =  'Successfully logout'
    return HttpResponseRedirect('/signin/')

import re
def signup(request):
    if request.user.is_authenticated():
        return HttpResponse('You are already logined.')
    
    if not request.POST:
        t = loader.get_template('register.html')
        context = RequestContext(request)
        context['form']=RegisterForm()
        return HttpResponse(t.render(context))
    
    if request.method == 'POST':
        username=request.POST.get('username','')
        username=smart_unicode(username, encoding='utf-8', strings_only=False, errors='strict')

        email=request.POST.get('email','')
        password=request.POST.get('password1','')
        
        name=request.POST.get('name','')
        name=smart_unicode(name, encoding='utf-8', strings_only=False, errors='strict')
        
        dept=request.POST.get('dept','')
        dept=smart_unicode(dept, encoding='utf-8', strings_only=False, errors='strict')
        
        position=request.POST.get('position','')
        position=smart_unicode(position, encoding='utf-8', strings_only=False, errors='strict')
    
    try:
#         username=form.cleaned_data['username']
#         email=form.cleaned_data['email']
#         password=form.cleaned_data['password1']
#         
#         name=smart_unicode(form.cleaned_data['name'], encoding='utf-8', strings_only=False, errors='strict')
#         dept=smart_unicode(form.cleaned_data['dept'], encoding='utf-8', strings_only=False, errors='strict')
#         position=smart_unicode(form.cleaned_data['position'], encoding='utf-8', strings_only=False, errors='strict')
#         
        #parameter validation
        username_valid= re.match('[\w0-9]*',username) and len(username) >= 3 and len(username) < 16
        
        password_valid=True
        password_valid=len(password) >= 6 
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
            #new_user.is_active = True
            new_user.last_name = name
            
            new_profile = UserProfile(user=new_user)
            new_profile.dept=dept
            new_profile.position=position
            try:
                my_emailer.send_activation_mail(new_user, new_profile)
                new_user.save()
                new_profile.save()
            except Exception as e:
                print "2 :" + str(e)
            
            request.session['message'] = username + ' Registered. Check your email and Click Activation Link.'
            return HttpResponseRedirect('/signin/')
    except Exception as e:
        print "3 :" + str(e)
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
    request.session['message'] = user_account.username + ' is Activated. '
    return HttpResponseRedirect('/signin/')
    

from hashlib import sha1
def encode(string) : 
  return sha1(string).hexdigest()
    