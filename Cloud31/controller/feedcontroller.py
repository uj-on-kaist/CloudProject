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
    context['load_type']='me'
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
            return return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    

def load_feed(request, user_name):
    if user_name is not '':
        return get_user_feed(request,user_name)
    return return_error('user_name is empty')



def load_my_timeline(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            timelines = UserTimeline.objects.filter(user=user).order_by('-update_date')
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        messages.append(timeline.message)
                except:
                    pass
            
            result['feeds']=process_messages(messages)
                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4))   

# def get_my_feed(request):
#     result=dict()
#     result['success']=True
#     result['message']='success'
#     
#     try:
#         user = User.objects.get(username=request.user.username)
#         try:
#             messages = Message.objects.filter(author=user,is_deleted=False).order_by('-reg_date')
#             result['feeds']=process_messages(messages)
#                 
#         except:
#             result['success']=True
#             result['message']='Do not have any message'
#     except:
#             result['success']=False
#             result['message']='no such user'
#             
#     return HttpResponse(json.dumps(result, indent=4))

def get_user_feed(request,user_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=user_name)
        try:
            messages = Message.objects.filter(author=user,is_deleted=False).order_by('-reg_date')
            result['feeds']=process_messages(messages)                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4))
    

def return_error(msg):
    result=dict()
    result['success']=False
    result['message']=msg
    return HttpResponse(json.dumps(result, indent=4))


import parser
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
            except:
                return return_error('Insert Failed')
                     
            try:
                author_timeline_new = UserTimeline(message=new_message,user=user)
                author_timeline_new.save()
            except:
                return return_error('Timelilne Failed')
                
            target_users=parser.detect_users(message)
            count = len(target_users)
            for i, user_name in enumerate(target_users):
                try:
                    target_user = User.objects.get(username=user_name)
                    target_user_timeline_new = UserTimeline(message=new_message,user=target_user)
                    target_user_timeline_new.save()
                    if i is not (count - 1):
                        new_message.related_users+=user_name+','
                    else:
                        new_message.related_users+=user_name
                except:
                    pass
            
            new_message.save()
            
            #TODO: UPDATE TARTGET_USER TIMELINE & TOPIC TIMELINE
            print parser.detect_topics(message)
        except:
            return return_error('No such User')
    
    return HttpResponse(json.dumps(result, indent=4))




    

def process_messages(messages):
    feeds=list()
    for message in messages:
        feed = dict()
        feed['id']=message.id
        feed['author']=message.author.username
        feed['contents']= parser.parse_text(message.contents)
        feed['attach_files']= message.attach_files
        feed['location']= message.location
        feed['reg_date']= str(message.reg_date)
        feeds.append(feed)
    
    return feeds

