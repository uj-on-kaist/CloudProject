#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.http import HttpResponseNotFound  


from controller.models import *

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode

from django.db.models import Q


import json
import parser
import my_utils


from controller.notificationcontroller import *

from pyofc2  import * 
import random
import time

from datetime import datetime
import datetime as dt
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
def overview(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
    t = loader.get_template('admin/overview.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['load_type']='me'
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_overview'] = "selected"
    
    
    now = datetime.now()
    year,month,day = now.year, now.month, now.day
    start_time = dt.date(year, month, day) - dt.timedelta(6)
    end_time = dt.date(year, month, day)  + dt.timedelta(1)
    
    context['user_length'] = User.objects.filter(is_active=True).count()
    context['feed_length'] = Message.objects.filter(is_deleted=False).count()
    context['topic_length'] = Topic.objects.all().count()
    context['file_length'] = File.objects.filter(is_attached=True).count()
    
    
    context['recent_messages'] = Message.objects.filter(is_deleted=False).order_by("-reg_date")[:5]
    context['recent_users'] = User.objects.filter(is_active=True).order_by("-last_login")[:5]
    return HttpResponse(t.render(context))

def stats_topic(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
    
    t = loader.get_template('admin/stats_topic.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_topic'] = 'selected'
    context['popular_topics'] = Topic.objects.all().order_by("-reference_count")[:20]
    
    context['side_list']=['search_topic']
    my_utils.prepare_search_topic(context)
    
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
        
        
        paginator = Paginator(topics, 5)
        
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
    
def stats_topic_detail(request ,topic_name):
    if not request.user.is_staff:
        return HttpResponseNotFound()
        
    t = loader.get_template('admin/stats_topic_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['popular_topics'] = Topic.objects.all().order_by("-reference_count")[:20]
    
    return HttpResponse(t.render(context))  

def stats_member(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()    
    t = loader.get_template('admin/stats_member.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_member'] = 'selected'
    
    return HttpResponse(t.render(context))      

def stats_member_detail(request, user_name):
    t = loader.get_template('admin/stats_topic_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['popular_topics'] = Topic.objects.all().order_by("-reference_count")[:20]
    
    return HttpResponse(t.render(context))  