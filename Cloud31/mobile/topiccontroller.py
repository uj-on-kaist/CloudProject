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



def popular(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['topics']=list()
    
    topics = Topic.objects.filter(reference_count__gt=0).order_by("-reference_count")[:20]
    for topic in topics:
        a_topic=dict()
        a_topic['id']=topic.id
        a_topic['topic_name']=topic.topic_name
        result['topics'].append(a_topic)
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def detail(request, topic_id):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        topic = Topic.objects.get(id=topic_id)
        
        topic_info = dict()
        topic_info['id']=topic.id
        topic_info['topic_name']=topic.topic_name
        topic_info['topic_desc']=topic.topic_detail
        related_users=my_utils.get_related_users(topic.topic_name)
        result['topic']=topic_info
        topic_info['related_users']=list()
        for user in related_users:
            user_info = dict()
            user_info['userID']=user.username
            user_info['picture']=user.picture_url
            topic_info['related_users'].append(user_info)
            
            
    except Exception as e:
        print str(e)
        return my_utils.return_error('Empty Message')
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def load_topic_timeline(request,topic_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        topic = Topic.objects.get(id=topic_id)
        try:
            timelines = TopicTimeline.objects.filter(additional, topic=topic).order_by('-update_date')[:DEFAULT_LOAD_LENGTH]
            if not timelines:
                result['feeds']=my_utils.process_messages(request, list())
                return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        timeline.message.base_id=timeline.id
                        messages.append(timeline.message)
                except:
                    pass
            
            if len(timelines) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
            
            result['feeds']=my_utils.process_messages(request, messages)
                
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such Topic')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')