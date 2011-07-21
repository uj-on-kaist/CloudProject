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

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils
from controller import parser

from django.views.decorators.csrf import csrf_exempt

def detail(request,username):
    result=dict()
    result['success']=True
    result['message']='success'
    result['user']=dict()
    try:
        user_info=dict()
        user = User.objects.get(username=username)
        try:
            user_profile = UserProfile.objects.get(user=user)
        except:
            return my_utils.return_error('Empty User')
        try:
            user_info['last_login']=str(user.last_login)
            user_info['email']=user.email
            user_info['userID']=user.username
            user_info['name']=user.last_name
            user_info['dept']=user_profile.dept
            user_info['position']=user_profile.position
            user_info['picture']= user_profile.picture.url
        except:
            user_info['author_picture']='/media/default.png'
        
        user_info['related_topics']=get_related_topics(user.username)
        
        result['user']=user_info
    except Exception as e:
        print str(e)
        return my_utils.return_error('Empty User')
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
def get_related_topics(username):
    result = list()
    
    try:
        user = User.objects.get(username=username)
    except:
        return result
    
    try:
        messages = Message.objects.filter(author=user)
        topic_list = ''
        for message in messages:
            if message.related_topics != '':
                topic_list += message.related_topics
                
        topics = filter(None,list(set(topic_list.split(','))))
    except Exception as e:
        print str(e)
        pass
        
    if topics:
        for topic_name in topics:
            try:
                topic =dict()
                a_topic = Topic.objects.get(topic_name=topic_name)
                topic['topic_name']=a_topic.topic_name
                topic['id']=a_topic.id
                result.append(topic)
            except:
                pass

    return result