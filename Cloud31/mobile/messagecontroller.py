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
from controller.notificationcontroller import *
from controller.messagecontroller import *


import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils
from controller import parser

from django.views.decorators.csrf import csrf_exempt


def get_message(request, message_id):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        message = DirectMessage.objects.filter(id=message_id)
        result['message']=process_messages(request, message)[0]
    except Exception as e:
        print str(e)
        return my_utils.return_error('Empty Message')
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')



@csrf_exempt
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

@csrf_exempt
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
            try:
                user_profile = UserProfile.objects.get(user=new_dm_reply.author)
                item['author_picture']= user_profile.picture.url
            except:
                item['author_picture']='/media/default.png'
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
    
    
@csrf_exempt
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