#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
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

from controller.notificationcontroller import *

DEFAULT_LOAD_LENGTH = 10


@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('message.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
#   user = get_object_or_404(User,username=request.user.username)
    
    context['page_dm'] = "selected"
    context['type'] = 'all'
    if request.GET.get('type',False):
        context['type'] = request.GET['type']
    
    return HttpResponse(t.render(context))

@login_required(login_url='/signin/')
def new(request):
    t = loader.get_template('message_new.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_dm'] = "selected"
    context['side_list']=['']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    return HttpResponse(t.render(context))
       
    

@login_required(login_url='/signin/')
def message_detail(request, message_id):
    t = loader.get_template('message_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return HttpResponseRedirect('signin')
    
    query_type = Q(author=user) | Q(receivers__contains=username)  
    try:
        d_message = DirectMessage.objects.filter(query_type,is_deleted=False,id=message_id)[0]
        context['message']=d_message
        context['message'].author_profile=UserProfile.objects.get(user=d_message.author)
        context['message'].contents=parser.parse_text(d_message.contents)
        context['message'].receivers=context['message'].receivers.replace(",", ", ")[:-2]
        context['message'].reg_date = d_message.reg_date.strftime('%Y-%m-%d %H:%M:%S')
        #2011-06-14 22:23:10
        context['type'] = 'all'
        if request.GET.get('type',False):
            context['type'] = request.GET['type']
    except Exception as e:
        print str(e)
        context['message']=None
        context['error_message'] = 'You cannot access to this message.'
        return HttpResponse(t.render(context))
        
    try:
        replies = DirectMessageReply.objects.filter(direct_message=d_message, is_deleted=False).order_by('reg_date')
        for reply in replies:
            reply.author_profile = UserProfile.objects.get(user=reply.author)
            reply.reg_date = reply.reg_date.strftime('%Y-%m-%d %H:%M:%S')
        context['replies']= replies
        print replies
    except Exception as e:
        print str(e)
    
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
        #SEND NOTIFICATION
        for receiver in receivers:
            try:
                target_user = User.objects.get(username=receiver)
                info = dict()
                info['from'] = user
                info['to'] = target_user
                info['target_object'] = new_dm
                register_noti(request, "new_dm",info)
            except:
                pass
    else:
        return my_utils.return_error('empty message')
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def reply_message(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    reply_message=''
    message_id=''
    if request.method == 'POST':
        if request.POST['message']:
            reply_message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST['message_id']:
            message_id=request.POST['message_id']
            
    print reply_message
    if message_id is '':
        return my_utils.return_error('No Message ID')

    if reply_message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Sign in first')
           
        try:
            user = User.objects.get(username=request.user.username)
            username = request.user.username
            username +=","
            query_type = Q(author=user) | Q(receivers__contains=username)
            d_message = DirectMessage.objects.filter(query_type,is_deleted=False,id=message_id)[0]
        except:
            return my_utils.return_error('You are now allowed to this message')
        
        try: 
            new_dm_reply = DirectMessageReply(direct_message=d_message,author=user,contents=reply_message)
            new_dm_reply.save()
            d_message.save()
        except:
            return my_utils.return_error('Send Reply Failure')
        
        try:
            item = dict()
            item['id']=new_dm_reply.id
            item['author']=new_dm_reply.author.username
            item['contents']= parser.parse_text(new_dm_reply.contents)
            item['reg_date']= str(new_dm_reply.reg_date)
            result['reply']=item
        except Exception as e:
            print str(e)
        
        #TODO : SEND NOTIFICATION TO USERS
        #SEND NOTIFICATION
        try:
            author_name = d_message.author.username
            target_user = User.objects.get(username=author_name)
            info = dict()
            info['from'] = user
            info['to'] = target_user
            info['target_object'] = d_message
            register_noti(request, "new_dm_reply",info)
        except:
            pass
    else:
        return my_utils.return_error('empty message')
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


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
        
    
    base_id = request.GET.get("base_id",False)
    additional = Q()
    if base_id:
        try:
            d_message = DirectMessage.objects.get(id=base_id)
            additional = Q(reg_date__lt=d_message.reg_date)
        except:
            pass

    try:
        d_messages = DirectMessage.objects.filter(query_type, additional,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        result['messages'] = process_messages(d_messages)
        
        if len(d_messages) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
    except Exception as e:
        print str(e)
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


def process_messages(messages):
    d_messages=list()
    for message in messages:
        d_message = dict()
        d_message['id']=message.id
        d_message['base_id']=message.id
        d_message['author']=message.author.username
        try:
            user_profile = UserProfile.objects.get(user=message.author)
            d_message['author_picture']= user_profile.picture.url
        except:
            d_message['author_picture']='/media/default.png'
            
        d_message['contents']= parser.parse_text(message.contents)
        d_message['receivers']= message.receivers.replace(",", ", ")[:-2]
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
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def delete_reply(request, reply_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            reply = DirectMessageReply.objects.get(author=user, id=reply_id)
            reply.is_deleted=True
            reply.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    