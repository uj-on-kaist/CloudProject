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

from django.db.models import Q

import json
import my_utils

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url='/signin/')
def topic(request):
    t = loader.get_template('topic.html')
    context = RequestContext(request)
    
    context['side_list']=['search_topic']
    my_utils.prepare_search_topic(context)
    
    context['page_topic'] = "selected"
    context['topics']=list()
    try:
        keyword = request.GET.get('q', '')
        query_type = Q()
        if keyword is not '':
            print keyword
            query_type = Q(topic_name__istartswith=keyword)
        
        search_index = request.GET.get('index', '')
        print search_index
        if search_index is not '':
            if search_index in map(chr, range(65, 91)):
                query_type = Q(topic_name__istartswith=search_index)
            elif search_index == 'number':
                query_type = Q(topic_name__gt="0",topic_name__lt="9")
            else:
                this_index,next_index=my_utils.next_search_index(search_index)
                query_type = Q(topic_name__gt=this_index, topic_name__lt=next_index)
        
        topics = Topic.objects.filter(query_type).order_by('topic_name')
        
        
        paginator = Paginator(topics, 15)
        
        page = request.GET.get('page', 1)
        try:
            context['topics'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['topics'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['topics'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['topics'].number, paginator.num_pages)
        
        
    except Exception as e:
        print str(e)
        
    
    return HttpResponse(t.render(context))
    
    
@login_required(login_url='/signin/')
def topic_detail(request,topic_name):
    t = loader.get_template('topic_detail.html')
    context = RequestContext(request)
    topic_name = smart_unicode(topic_name, encoding='utf-8', strings_only=False, errors='strict')
    context['side_list']=['topic_detail']
    context['topic']=list()
    try:
        context['topic'] = Topic.objects.filter(topic_name=topic_name)[0]
    except Exception as e:
        pass
    
    context['page_topic'] = "selected"
    context['load_type']='topic#' + topic_name
    context['topic_name']=context['topic'].topic_name
    
    
    context['related_users']=my_utils.get_related_users(context['topic'].topic_name)
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
    
    


def update_description(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    topic_id = request.POST.get('topic_id',False)
    new_description = request.POST.get('desc',False)
    new_description = smart_unicode(new_description, encoding='utf-8', strings_only=False, errors='strict')

    try:
        topic = Topic.objects.get(id=topic_id)
        topic.topic_detail = new_description
        topic.save()
    except Exception as e:
        print str(e)
    
    return HttpResponse(json.dumps(result, indent=4))
    