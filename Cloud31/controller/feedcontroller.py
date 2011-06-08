#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode


import json

@login_required(login_url='/signin/')
def feed(request):
    t = loader.get_template('feed.html')
    context = RequestContext(request)
    return HttpResponse(t.render(context))
    
    
def get_my_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
    except:
            result['success']=False
            result['message']='no such user'
            
    return HttpResponse(json.dumps(result, indent=4))


def update_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    message=''
    attach_list=''
    location_info=''
    if request.method == 'POST':
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['attach_list']:
            attach_list=request.POST['attach_list']
            
        if request.POST['location_info']:
            attach_list=request.POST['location_info']
        
    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
            try: 
                new_message = Message(author=user,contents=message,location=location_info,attach_files=attach_list)
                new_message.save()
                
                #TODO: UPDATE USER_TIMELINE & TARTGET_USER TIMELINE & TOPIC TIMELINE
            except:
                result['success']=False
                result['message']='Insert Failed'
        except:
            result['success']=False
            result['message']='no such user'
    
    return HttpResponse(json.dumps(result, indent=4))




