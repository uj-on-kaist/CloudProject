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
    

def delete_feed(request, feed_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            message = Message.objects.get(author=user, id=feed_id)
            message.is_deleted=True
            message.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            result['success']=False
            result['message']='Please sign in first'
            
    return HttpResponse(json.dumps(result, indent=4))
    

def load_feed(request, load_type):
    if load_type == 'me':
        return get_my_feed(request)
    

def process_messages(messages):
    feeds=list()
    for message in messages:
        feed = dict()
        feed['id']=message.id
        feed['author']=message.author.username
        feed['contents']= message.contents
        feed['attach_files']= message.attach_files
        feed['location']= message.location
        feed['reg_date']= str(message.reg_date)
        feeds.append(feed)
    
    return feeds

def get_my_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            messages = Message.objects.filter(author=user,is_deleted=False).order_by('-reg_date')
            result['feeds']=process_messages(messages)
                
        except:
            result['success']=True
            result['message']='Do not have any message'
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




