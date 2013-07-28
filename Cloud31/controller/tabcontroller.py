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
import my_utils, my_emailer


from controller.notificationcontroller import *
from controller.statisticcontroller import *

from pyofc2  import * 
import random
import time

from datetime import datetime
import datetime as dt
from django.db.models import Q
from django.db.models import Count


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def tab(request):
    if not request.user.is_staff:
        return HttpResponseNotFound() 
    t = loader.get_template('admin/tab.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_tab'] = "selected"
    
    tab_name = request.POST.get('tab_name', '')
    is_public = request.POST.get('is_public', False)
    
    if tab_name is not '':
        ## create tab
        try:
            new_tab = Tab(name=tab_name, is_public=is_public)
            new_tab.save()
            context['tab_message'] = "Tab \'" + tab_name + "\' is created."
        except Exception as e:
            print e
            context['tab_message'] = "Tab \'" + tab_name + "\' is not created. Check again."
        
    
    tabs = Tab.objects.all()
    paginator = Paginator(tabs, 10)
        
    page = request.GET.get('page', 1)
    try:
        context['tabs'] = paginator.page(page)
    except PageNotAnInteger:
        context['tabs'] = paginator.page(1)
    except EmptyPage:
        context['tabs'] = paginator.page(paginator.num_pages)
    context['index_info'] = my_utils.get_index_list(context['tabs'].number, paginator.num_pages)
    
    return HttpResponse(t.render(context))

def tab_delete(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()

    tab_id = request.POST.get('tab_id','')
    if tab_id is not '':
        try:
            tab = Tab.objects.get(id=tab_id)
            tab.delete()
        except Exception as e:
            print e
    
    return HttpResponseRedirect("/admin/tab/")

def tab_manage(request, tab_id):
    if not request.user.is_staff:
        return HttpResponseNotFound()
    
    t = loader.get_template('admin/tab_manage.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_tab'] = "selected"
    
    tab = get_object_or_404(Tab, id=tab_id, is_public=False)
    
    context['tab_name'] = tab.name
    context['tab_id'] = tab.id
    
    
    if request.POST.get('add_user', False):
        try:
            username = request.POST.get('add_user', '')
            new_user = User.objects.get(username=username)
            new_relation = TabUsers.objects.get_or_create(tab=tab,user=new_user)[0]
            new_relation.save()
        except:
            print 'add failed'
    
    if request.POST.get('delete_user', False):
        try:
            username = request.POST.get('delete_user', '')
            user = User.objects.get(username=username)
            relation = TabUsers.objects.get(tab=tab,user=user)
            relation.delete()
        except:
            print 'add failed'
    
    
    tab_users = TabUsers.objects.filter(tab=tab)
    
    paginator_tab = Paginator(tab_users, 10)
        
    tab_page = request.GET.get('tab_page', 1)
    
    try:
        context['tab_users'] = paginator_tab.page(tab_page)
    except PageNotAnInteger:
        context['tab_users'] = paginator_tab.page(1)
    except EmptyPage:
        context['tab_users'] = paginator_tab.page(paginator_tab.num_pages)
    context['index_info_tab'] = my_utils.get_index_list(context['tab_users'].number, paginator_tab.num_pages)
    
    
    
    users = UserProfile.objects.filter(is_deactivated=False,user__is_active=True)
    
    paginator = Paginator(users, 10)
    page = request.GET.get('page', 1)
    try:
        context['users'] = paginator.page(page)
    except PageNotAnInteger:
        context['users'] = paginator.page(1)
    except EmptyPage:
        context['users'] = paginator.page(paginator.num_pages)
    context['index_info'] = my_utils.get_index_list(context['users'].number, paginator.num_pages)
    
    
    context['tab_page'] = tab_page
    context['index'] = page
    
    return HttpResponse(t.render(context))