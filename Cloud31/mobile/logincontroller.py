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

from django.conf import settings

from controller import my_emailer
from controller import my_utils

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signin(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    userID = request.POST.get('userID',False)
    userPW = request.POST.get('userPW',False)
    deviceToken = request.POST.get('deviceToken',False)
    print deviceToken
    if not userID or not userPW:
        return my_utils.return_error('Check Inputs')
    
    try:
        user = authenticate(username=userID,password=userPW)
        if user is not None:
            user_profile = UserProfile.objects.get(user=user)
            if user.is_active and not user_profile.is_deactivated:
                login(request, user)
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    user_profile.device_id = deviceToken
                    user_profile.save()
                except Exception as e:
                    print str(e)

            else:
                return my_utils.return_error('That User is not Active')
            user_profile = UserProfile.objects.get(user=user)
            result['profile']=dict()
            try:
                result['profile']['username']= user.last_name
                result['profile']['picture']= user_profile.picture.url
            except:
                 result['profile']['picture']='/media/default.png'
            
        else:
            return my_utils.return_error('Signin Failed')
    except Exception as e:
        print str(e)
        return my_utils.return_error('Error Occured')
        
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
def login_test(request):
    result=dict()
    result['success']=True
    result['message']='success'
    if not request.user.id:
        return my_utils.return_error('Sign In First')
    try:
        user = User.objects.get(id=request.user.id)
        print user.username
        profile=UserProfile.objects.get(user=user)
        result['picture'] = profile.picture.url
        result['username'] = user.last_name
        result['dept'] = profile.dept
        result['position'] = profile.position
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    except Exception as e:
        print str(e)
        pass
    return my_utils.return_error('Error Occured')
    
def signout(request):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.device_id = ''
        user_profile.save()
    except Exception as e:
        print str(e)
    logout(request)
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
    