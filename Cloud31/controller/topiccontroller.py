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
import my_utils

@login_required(login_url='/signin/')
def topic(request):
    t = loader.get_template('topic.html')
    context = RequestContext(request)
    context['topics']=list()
    try:
        context['topics'] = Topic.objects.all()[:5]
    except Exception as e:
        print str(e)
        
    
    return HttpResponse(t.render(context))
    
    
@login_required(login_url='/signin/')
def topic_detail(request,topic_name):
    t = loader.get_template('topic_detail.html')
    context = RequestContext(request)
    topic_name = smart_unicode(topic_name, encoding='utf-8', strings_only=False, errors='strict')
    context['topics']=list()
    try:
        context['topics'] = Topic.objects.filter(topic_name=topic_name)
    except Exception as e:
        print str(e)
    context['load_type']='topic#' + topic_name
    context['topic_name']=context['topics'][0].topic_name
    return HttpResponse(t.render(context))
    
    
def load_topic_timeline(request,topic_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        topic = Topic.objects.get(topic_name=topic_name)
        try:
            timelines = TopicTimeline.objects.filter(topic=topic).order_by('-update_date')
            if not timelines:
                return return_error('No Such Topic #2') 
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        messages.append(timeline.message)
                except:
                    pass
            
            result['feeds']=my_utils.process_messages(request, messages)
                
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Do not have any message'
    except:
            return return_error('No Such Topic')
            
    return HttpResponse(json.dumps(result, indent=4))