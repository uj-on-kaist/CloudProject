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



def test(request):
    t = title(text=time.strftime('%a %Y %b %d'))
    b1 = bar()
    b1.values = range(9,0,-1)
    b2 = bar()
    b2.values = [random.randint(0,9) for i in range(9)]
    b2.colour = '#56acde'
    chart = open_flash_chart()
    chart.title = t    
    chart.add_element(b1)
    chart.add_element(b2)
    return HttpResponse(chart.render())
    
    
def overview(request):
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
    
    context['user_length'] = User.objects.filter(last_login__range=(start_time,end_time) \
                                                ,is_active=True).count()
    context['feed_length'] = Message.objects.filter(reg_date__range=(start_time,end_time) \
                                                ,is_deleted=False).count()
    context['topic_length'] = Topic.objects.filter(reg_date__range=(start_time,end_time)).count()
    context['file_length'] = File.objects.filter(upload_date__range=(start_time,end_time) \
                                                ,is_attached=True).count()
    
    
    context['recent_messages'] = Message.objects.filter(reg_date__range=(start_time,end_time) \
                        ,is_deleted=False).order_by("-reg_date")[:5]
    context['recent_users'] = User.objects.filter(last_login__range=(start_time,end_time) \
                        ,is_active=True).order_by("-last_login")[:5]
    return HttpResponse(t.render(context))
    

def recent_user_graph(request):
    if not request.user.is_staff:
        return my_utils.return_error('You cannot access to this')
    
    year = request.GET.get("year", False)
    month = request.GET.get("month", False)
    day = request.GET.get("day", False)
    
    if not (year and month and day):
        now = datetime.now()
        year,month,day = now.year, now.month, now.day
    
    date_before = 6
    range_const = 1
    
    end_time = dt.date(year, month, day)
    start_time = end_time - dt.timedelta(date_before)
    
    data = list()
    time = start_time
    label_list = list()
    
    while time <= end_time:
        next_time = time + dt.timedelta(range_const)
        data.append(User.objects.filter(last_login__range=(time, next_time)).count())
        label_list.append((" "+str(time.month)+"/"+str(time.day)+" <br>"+str(time.year)).replace("-","/"))
        time = next_time
    
    t = title(text="<b>Recent Users From "+str(start_time)+" to "+str(end_time)+"</b>")
    t.style = "{font-size: 12px; font-weight: bold; text-align: center;padding-bottom:5px;}"
    l = line()
    l.values = data
    chart = open_flash_chart()
    chart.title = t
    
    x = x_axis()
    x.style = "{text-align:center}"
    lbl = labels(labels=label_list)
    lbl.steps = int(len(data) / 3)
    x.labels = lbl
    x.steps = int(len(data) / 6)
    chart.x_axis = x
    chart.add_element(l)
    return HttpResponse(chart.render())


def recent_message_graph(request):
    if not request.user.is_staff:
        return my_utils.return_error('You cannot access to this')
    
    year = request.GET.get("year", False)
    month = request.GET.get("month", False)
    day = request.GET.get("day", False)
    
    if not (year and month and day):
        now = datetime.now()
        year,month,day = now.year, now.month, now.day
    
    date_before = 6
    range_const = 1
    
    end_time = dt.date(year, month, day)
    start_time = end_time - dt.timedelta(date_before)
    
    data = list()
    time = start_time
    label_list = list()
    
    while time <= end_time:
        next_time = time + dt.timedelta(range_const)
        data.append(Message.objects.filter(is_deleted=False,reg_date__range=(time, next_time)).count())
        label_list.append((" "+str(time.month)+"/"+str(time.day)+" <br>"+str(time.year)).replace("-","/"))
        time = next_time
    
    t = title(text="<b>Recent Message From "+str(start_time)+" to "+str(end_time)+"</b>")
    t.style = "{font-size: 12px; font-weight: bold; text-align: center;padding-bottom:5px;}"
    l = line()
    l.values = data
    chart = open_flash_chart()
    chart.title = t
    
    x = x_axis()
    x.style = "{text-align:center}"
    lbl = labels(labels=label_list)
    lbl.steps = int(len(data) / 3)
    lbl.style = "{text-align:center}"
    x.labels = lbl
    x.steps = int(len(data) / 6)
    chart.x_axis = x
    chart.add_element(l)
    return HttpResponse(chart.render())

    