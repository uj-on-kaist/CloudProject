#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core import serializers

from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode
from django.db.models import Q

import json
import my_utils
import parser

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('message.html')
    context = RequestContext(request)
#     user = get_object_or_404(User,username=request.user.username)
    
    context['type'] = 'all'
    if request.GET.get('type',False):
        context['type'] = request.GET['type']
    
    return HttpResponse(t.render(context))
    
    

@login_required(login_url='/signin/')
def message_detail(request, message_id):
    t = loader.get_template('message_detail.html')
    context = RequestContext(request)
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return HttpResponseRedirect('signin')
    
    query_type = Q(author=user) | Q(receivers__contains=username)  
    d_message = DirectMessage.objects.filter(query_type,is_deleted=False,id=message_id)[0]
    context['message']=d_message
    context['message'].contents=parser.parse_text(d_message.contents)
    
    context['type'] = 'all'
    if request.GET.get('type',False):
        context['type'] = request.GET['type']
    
    return HttpResponse(t.render(context))

    
    
def send_message(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    receivers_text=''
    message=''
    if request.method == 'POST':
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['receivers']:
            receivers_text=request.POST['receivers']
            
    print message
    receivers = parser.detect_users(receivers_text)
    
    receiver_list=''
    for receiver in receivers:
        receiver_list += receiver + ','
    print receiver_list
    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Sign in first')
            
        try: 
            new_dm = DirectMessage(author=user,contents=message)
            new_dm.receivers = receiver_list
            new_dm.save()
        except:
            return my_utils.return_error('Send Message Failure')
            
            
        #TODO : SEND NOTIFICATION TO USERS
            
    else:
        return my_utils.return_error('empty message')
    return HttpResponse(json.dumps(result, indent=4))
    

def load_message(request, load_type):
    result=dict()
    result['success']=True
    result['error_message']='success'
    result['messages']=list()
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return my_utils.return_error('Sign in first')
    
    if load_type == 'all':
        query_type = Q(author=user) | Q(receivers__contains=username)
    elif load_type == 'sent':
        query_type = Q(author=user)
    elif load_type == 'received':
        query_type = Q(receivers__contains=username)    
    try:
        d_messages = DirectMessage.objects.filter(query_type, is_deleted=False).order_by('-reg_date')
        result['messages'] = process_messages(d_messages)
    except Exception as e:
        print str(e)
    
    return HttpResponse(json.dumps(result, indent=4))


def process_messages(messages):
    d_messages=list()
    for message in messages:
        d_message = dict()
        d_message['id']=message.id
        d_message['author']=message.author.username
        d_message['contents']= parser.parse_text(message.contents)
        d_message['receivers']= message.receivers
        d_message['reg_date']= str(message.reg_date)
        d_messages.append(d_message)
    return d_messages
    
    

def delete_message(request, message_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            message = DirectMessage.objects.get(author=user, id=message_id)
            message.is_deleted=True
            message.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    