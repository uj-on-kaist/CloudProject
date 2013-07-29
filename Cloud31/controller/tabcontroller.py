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


def tab_admin(request):
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
    
    
    tab_users = TabUsers.objects.filter(tab=tab).order_by("-reg_date")
    
    paginator_tab = Paginator(tab_users, 5)
        
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


@login_required(login_url='/signin/')
def tab(request):
    t = loader.get_template('tab.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['side_list']=['']
    context['page_tab_user'] = "selected"
    
    
    tabs = Tab.objects.all()
    user_tabs = list()
    for tab in tabs:
        try:
            if tab.is_public:
                user_tabs.append(tab)
            tab_user = TabUsers.objects.filter(tab=tab, user=request.user).count()
            if tab_user is not 0:
                user_tabs.append(tab)
        except Exception as e:
            print e
    paginator = Paginator(user_tabs, 10)
        
    page = request.GET.get('page', 1)
    try:
        context['tabs'] = paginator.page(page)
    except PageNotAnInteger:
        context['tabs'] = paginator.page(1)
    except EmptyPage:
        context['tabs'] = paginator.page(paginator.num_pages)
    context['index_info'] = my_utils.get_index_list(context['tabs'].number, paginator.num_pages)
    
    return HttpResponse(t.render(context))


@login_required(login_url='/signin/')
def tab_detail(request,tab_id):
    t = loader.get_template('tab_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_tab_user'] = "selected"
    
    print tab_id
    print tab_id
    tab = get_object_or_404(Tab, id=tab_id)
    
    context['tab'] = tab
    context['tab_name'] = tab.name
    context['tab_id'] = tab.id
    
    related_users = list()
    if not tab.is_public:
        tab_users = TabUsers.objects.filter(tab=tab)
        for tab_users in tab_users:
            user = tab_users.user
            if not user.is_active:
                continue
            try:
                user_profile = UserProfile.objects.get(user=user)
                user.picture_url = user_profile.picture.url
            except Exception as e:
                print str(e)
                user.picture_url = '/media/default.png'
            related_users.append(user)
    
    context['related_users'] = related_users
    
    context['side_list']=['tab_info']
    context['page_tab'] = "selected"
    
    return HttpResponse(t.render(context))






def delete_tab_feed(request, feed_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            message = TabFeed.objects.get(author=user, id=feed_id)
            message.is_deleted=True
            message.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def delete_tab_comment(request, comment_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            comment = TabComment.objects.get(author=user, id=comment_id)
            comment.is_deleted=True
            comment.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


def update_tab_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    message=''
    attach_list=''
    location_info=''
    lat = ''
    lng = ''
    if request.method == 'POST':
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['attach_list']:
            attach_list=request.POST['attach_list']
            
        if request.POST['location_info']:
            location_info=request.POST['location_info']
            try:
                location = location_info.split("|")
                lat = location[0]
                lng = location[1]
            except:
                pass
    tab_id = request.POST.get('tab',-1)
    if tab_id is -1:
        return my_utils.return_error('Empty Tab')

    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
            tab = Tab.objects.get(id=tab_id)
            print location_info
            try: 
                new_message = TabFeed(author=user,tab=tab,contents=message,lat=lat,lng=lng,attach_files=attach_list)
                new_message.save()   
            except:
                return my_utils.return_error('Insert Failed')
            
            
            #FILE CHECK
            attach_arr = attach_list.split('.')
            for attach_id in attach_arr:
                try:
                    if attach_id is '':
                        continue
                    attach = File.objects.get(id=attach_id)
                    attach.is_attached=True
                    attach.save()
                except Exception as e:
                    print str(e)
        except:
            return my_utils.return_error('No such User')
    else:
        return my_utils.return_error('Empty Message')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


def update_tab_comment(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    input_message=''
    if request.method == 'POST':
        if request.POST['message']:
            input_message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST['feed_id']:
            feed_id = request.POST['feed_id']

    if input_message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Please Sign in first')
        
        try:
            message = TabFeed.objects.filter(id=feed_id,is_deleted=False)[0]
        except:
            return my_utils.return_error('No such Message')
            
        try: 
            new_comment = TabComment(author=user,contents=input_message,message=message)
            new_comment.save()
            message.save()
        except:
            return my_utils.return_error('Insert Failed')
        
    else:
        return my_utils.return_error('Empty Message')
    
    try:
        item = dict()
        item['id']=new_comment.id
        item['author']=new_comment.author.username
        #item['author_picture']=UserProfile.objects.get(user=new_comment.author).picture.url
        item['author_picture']=my_utils.get_user_thumbnail(new_comment.author)
        item['author_name']=new_comment.author.last_name
        item['contents']= parser.parse_text(new_comment.contents)
        item['reg_date']= str(new_comment.reg_date)
        result['comment']=item
    except Exception as e:
        print str(e)
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

@never_cache
def load_tab_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        tab_id = request.GET.get("tab",-1)
        tab = Tab.objects.get(id=tab_id)
        base_id = request.GET.get("base_id",False)
        to_id = request.GET.get("to_id",False)
        sort_method = request.GET.get("sort","reg_date")
        additional = Q()
        load_length = DEFAULT_LOAD_LENGTH
        if base_id:
            try:
                if sort_method == 'reg_date':
                    message = TabFeed.objects.get(id=base_id, tab=tab)
                    additional = Q(reg_date__lt=message.reg_date)
                else:
                    message = TabFeed.objects.get(id=base_id, tab=tab)
                    additional = Q(update_date__lt=message.update_date)
            except:
                pass
            #additional = Q(id__lt=base_id)
        if to_id:
            load_length = 10000
            additional = Q(id__gte=base_id)
        
        
        if sort_method == 'reg_date':
            messages = TabFeed.objects.filter(additional,is_deleted=False,tab=tab).order_by('-reg_date')[:load_length]
        else:
            messages = TabFeed.objects.filter(additional,is_deleted=False,tab=tab).order_by('-update_date')[:load_length]
        
        
        result['feeds']=my_utils.process_tab_messages(request,messages)
        
        if len(messages) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
    except Exception as e:
        print str(e)
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

