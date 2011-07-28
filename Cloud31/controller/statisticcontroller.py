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

from django.db.models import Count

import random

def recent_user_graph(request):
    if not request.user.is_staff:
        return my_utils.return_error('You cannot access to this')
    
    date_before = 90
    range_const = 1
    
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
        
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
        
    
    data = list()
    time = start_time
    label_list = list()

    while time < end_time:
        next_time = time + dt.timedelta(range_const)
        data.append(UserLoginHistory.objects.filter(login_date__range=(time, next_time)).count())
        label_list.append(time.strftime("%B %d, %Y"))
        time = next_time
    
    #t = title(text="Data From "+start_time.strftime("%B %d, %Y")+" - To "+end_time.strftime("%B %d, %Y")+"")
    #t.style = "{font-size: 12px;text-align: right;padding-bottom:5px;}"
    l = line()
    l.values = data
    l.colour = "#325AAA"
    l.tip = "#x_label#<br>#val# Users Logined"
    chart = open_flash_chart()
    #chart.title = t
    
    y = y_axis()
    y.steps = 5
    chart.y_axis = y
    
    x = x_axis()
    lbl = x_axis_labels(steps=30,labels=label_list)
    x.labels = lbl
    x.steps = 15
    chart.x_axis = x
    chart.bg_colour = '#FAFAFA'
    chart.add_element(l)
    
    return HttpResponse(chart.render())


def now_datetime():
    now = dt.datetime.now() + dt.timedelta(1)
    result = dt.date(now.year, now.month, now.day)
    return result

def recent_message_graph(request):
    if not request.user.is_staff:
        return my_utils.return_error('You cannot access to this')
    
    date_before = 90
    range_const = 1
    
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
        
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
        
    
    data = list()
    time = start_time
    label_list = list()
    
    
    y = y_axis()
    y.min, y.max, y.steps = 0, 20, 5
    
    accu = request.GET.get("accu", False)
    if accu == "1":
        count = Message.objects.filter(is_deleted=False,reg_date__lt=time).count()
        while time < end_time:
            next_time = time + dt.timedelta(range_const)
            count+=Message.objects.filter(is_deleted=False,reg_date__range=(time, next_time)).count()
            data.append(count)
            if count > y.max:
                y.max = count+5
            label_list.append(time.strftime("%B %d, %Y"))
            time = next_time
    else:
        while time < end_time:
            next_time = time + dt.timedelta(range_const)
            count = Message.objects.filter(is_deleted=False,reg_date__range=(time, next_time)).count()
            data.append(count)
            if count > y.max:
                y.max = count+5
            label_list.append(time.strftime("%B %d, %Y"))
            time = next_time

    l = line()
    l.tip = "#x_label#<br>#val# Feeds"
    l.values = data
    l.colour = "#325AAA"
    chart = open_flash_chart()
        
    chart.y_axis = y
    
    x = x_axis()
    lbl = x_axis_labels(steps=date_before/3,labels=label_list)
    
    x.labels = lbl
    x.steps = int(date_before / 6)
    if x.steps < 1:
        x.steps = 1
    chart.x_axis = x
    chart.bg_colour = '#FAFAFA'
    chart.add_element(l)    
    return HttpResponse(chart.render())


def get_start_end_time(in_start,in_end):
    start = in_start.split("-")
    start_time = dt.date(int(start[0]),int(start[1]),int(start[2]))
    end = in_end.split("-")
    end_time = dt.date(int(end[0]),int(end[1]),int(end[2])+1)
    delta = end_time - start_time
    date_before = delta.days
    return start_time, end_time, delta, date_before

def recent_pop_topics(request):
    date_before = 90
    range_const = 1
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
        
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
    
    accu = request.GET.get("accu", False)
    if accu == "1":
        topics = TopicTimeline.objects.filter(message__is_deleted=False,message__reg_date__range=(start_time, end_time), topic__topic_name__gt='').values('topic').annotate(topic_count=Count('topic')).order_by("-topic_count")[:10]
        
        x = x_axis()
        y = y_axis()
        y.min, y.max, y.steps = 0, 5, 5
        chart = open_flash_chart()
        chart.y_axis = y
        for item in topics:
            try:
                topic = Topic.objects.get(id=item['topic'])
                data = list()
                time = start_time
                label_list = list()
                while time < end_time:
                    next_time = time + dt.timedelta(range_const)
                    count = Message.objects.filter(reg_date__range=(time,next_time),is_deleted=False,related_topics__contains=topic.topic_name).count()
                    #count = TopicTimeline.objects.filter(topic=topic,update_date__range=(time, next_time)).count()
                    data.append(count)
                    if count > y.max:
                        y.max = count+5
                    label_list.append(time.strftime("%B %d, %Y"))
                    time = next_time
                l = line()
                l.tip = topic.topic_name+"<br>#val# Feeds"
                l.values = data
                l.colour = "#" + "%x" % random.randint(0,255) + "%x" % random.randint(0,255) + "%x" % random.randint(0,255)
                l.text = "#" + topic.topic_name
                chart.add_element(l)
            except:
                pass
        
        lbl = x_axis_labels(steps=date_before/3,labels=label_list)
        x.labels = lbl
        x.steps = int(date_before / 6)
        if x.steps < 1:
            x.steps = 1
        chart.x_axis = x
        chart.bg_colour = '#FAFAFA'
            
        return HttpResponse(chart.render())
        
    else:
        topics = TopicTimeline.objects.filter(update_date__range=(start_time, end_time), topic__topic_name__gt='').values('topic').annotate(topic_count=Count('topic')).order_by("-topic_count")[:10]
    
        values = list()
        total = 0
        for item in topics:
            total += int(item['topic_count'])
            
        for item in topics:
            try:
                topic = Topic.objects.get(id=item['topic'])
                value = pie_value(label="#"+topic.topic_name, value=item['topic_count'])
                value.tip = "#label#<br> #val# Feeds ("+str("%.2f" % (float(item['topic_count'])*100.0/total))+"%)"
                values.append(value)
            except:
                pass
        p = pie()
        p.values = values
        p.tip = "#label#<br>#val# Feeds"
        chart = open_flash_chart()
        chart.bg_colour = '#FAFAFA'
        chart.add_element(p)
    
        t = title(text=str(total)+" Total Feeds")
        t.style = "{font-size: 12px;text-align: right;padding-bottom:5px;}"
        chart.title = t
        return HttpResponse(chart.render())

        
    

def recent_active_users(request):
    date_before = 90
    
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
        
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
        
    users = Message.objects.filter(is_deleted=False,reg_date__range=(start_time, end_time)).values('author').annotate(author_count=Count('author')).order_by("-author_count")[:10]
    
    values = list()
    total = 0
    for item in users:
        total += int(item['author_count'])
        
    for item in users:
        author = User.objects.get(id=item['author'])
        value = pie_value(label="@"+author.username, value=item['author_count'])
        value.tip = "#label# ("+author.last_name+")<br>#val# Feeds ("+str("%.2f" % (float(item['author_count'])*100.0/total))+"%)"
        values.append(value)

    p = pie()
    #values = [ pie_value(label="crap", value=4), pie_value(label="face", value=20)]
    p.values = values
    p.tip = "#label#<br>#val# Feeds"
    #p.colours = ['#1C9E05','#FF368D']
    chart = open_flash_chart()
    chart.bg_colour = '#FAFAFA'
    chart.add_element(p)
    
    t = title(text=str(total)+" Total Feeds")
    t.style = "{font-size: 12px;text-align: right;padding-bottom:5px;}"
    chart.title = t
    return HttpResponse(chart.render())

def recent_user_stats(request, user_id):
    date_before = 90
    range_const = 1
    
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
    
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
    
    data = list()
    time = start_time
    label_list = list()
    
    
    y = y_axis()
    y.min, y.max, y.steps = 0, 10, 5
    
    accu = request.GET.get("accu", False)
    try:
        user = User.objects.get(id=user_id)
        if accu == "1":
            count = Message.objects.filter(is_deleted=False,author=user,reg_date__lt=time).count()
            while time < end_time:
                next_time = time + dt.timedelta(range_const)
                count+=Message.objects.filter(is_deleted=False,author=user,reg_date__range=(time, next_time)).count()
                data.append(count)
                if count > y.max:
                    y.max = count+5
                label_list.append(time.strftime("%B %d, %Y"))
                time = next_time
        else:
            while time < end_time:
                next_time = time + dt.timedelta(range_const)
                count = Message.objects.filter(is_deleted=False,author=user,reg_date__range=(time, next_time)).count()
                data.append(count)
                if count > y.max:
                    y.max = count+5
                label_list.append(time.strftime("%B %d, %Y"))
                time = next_time
                
    except Exception as e:
        print str(e)
        chart = open_flash_chart()
        return HttpResponse(chart.render())
        
    l = line()
    l.tip = "#x_label#<br>#val# Feeds"
    l.values = data
    l.colour = "#325AAA"
    chart = open_flash_chart()
        
    chart.y_axis = y
    
    x = x_axis()
    lbl = x_axis_labels(steps=date_before/3,labels=label_list)
    x.labels = lbl
    x.steps = int(date_before / 6)
    if x.steps < 1:
        x.steps = 1
    chart.x_axis = x
    chart.bg_colour = '#FAFAFA'
    chart.add_element(l)
    
    t = title(text="User @"+user.username)
    t.style = "{font-size: 12px;text-align: center;padding:5px 0px 5px 0; color: #325AAA; font-weight:bold;}"
    chart.title = t
    
    return HttpResponse(chart.render())
    
def recent_topic_stats(request, topic_id):
    date_before = 90
    range_const = 1
    
    end_time = now_datetime()
    start_time = end_time - dt.timedelta(date_before)
    
    in_start =request.GET.get("start",False)
    in_end = request.GET.get("end",False)
    
    if in_start and in_end:
        start_time, end_time, delta, date_before = get_start_end_time(in_start, in_end)
    
    data = list()
    time = start_time
    label_list = list()
    
    
    y = y_axis()
    y.min, y.max, y.steps = 0, 10, 5
    
    accu = request.GET.get("accu", False)
    try:
        topic = Topic.objects.get(id=topic_id)
        if accu == "1":
            count = TopicTimeline.objects.filter(topic=topic,update_date__lt=time).count()
            while time < end_time:
                next_time = time + dt.timedelta(range_const)
                count+=TopicTimeline.objects.filter(topic=topic,update_date__range=(time, next_time)).count()
                data.append(count)
                if count > y.max:
                    y.max = count+5
                label_list.append(time.strftime("%B %d, %Y"))
                time = next_time
        else:
            while time < end_time:
                next_time = time + dt.timedelta(range_const)
                count = TopicTimeline.objects.filter(topic=topic,update_date__range=(time, next_time)).count()
                data.append(count)
                if count > y.max:
                    y.max = count+5
                label_list.append(time.strftime("%B %d, %Y"))
                time = next_time
                
    except Exception as e:
        print str(e)
        chart = open_flash_chart()
        return HttpResponse(chart.render())
        
    l = line()
    l.tip = "#x_label#<br>#val# Feeds"
    l.values = data
    l.colour = "#325AAA"
    chart = open_flash_chart()
        
    chart.y_axis = y
    
    x = x_axis()
    lbl = x_axis_labels(steps=date_before/3,labels=label_list)
    x.labels = lbl
    x.steps = int(date_before / 6)
    if x.steps < 1:
        x.steps = 1
    
    chart.x_axis = x
    chart.bg_colour = '#FAFAFA'
    chart.add_element(l)
    
    t = title(text="Topic #"+topic.topic_name)
    t.style = "{font-size: 12px;text-align: center;padding:5px 0px 5px 0; color: #325AAA; font-weight:bold;}"
    chart.title = t
    
    return HttpResponse(chart.render())