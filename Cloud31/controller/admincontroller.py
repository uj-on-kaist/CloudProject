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

from pyofc2  import * 
import random
import time

from datetime import datetime
import datetime as dt
from django.db.models import Q
from django.db.models import Count


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def export(request):
    if not request.user.is_staff:
        return HttpResponseNotFound() 
    t = loader.get_template('admin/export.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_export'] = "selected"
    
    start_date=request.GET.get('start','')
    end_date=request.GET.get('end','')
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    if start_date == '':
        start_date=this_week_start.strftime("%Y-%m-%d")
    if end_date == '':
        end_date=this_week_end.strftime("%Y-%m-%d")
    
    context['start_date']=start_date
    context['end_date']=end_date
    
    return HttpResponse(t.render(context))




def invite(request):
    if not request.user.is_staff:
        return HttpResponseNotFound() 
    t = loader.get_template('admin/invite/invite.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_invite'] = "selected"
    
    return HttpResponse(t.render(context))
    

    
def overview(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
    t = loader.get_template('admin/overview.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['load_type']='me'
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_overview'] = "selected"
    
    
    now = datetime.now()
    year,month,day = now.year, now.month, now.day
    start_time = dt.date(year, month, day) - dt.timedelta(6)
    end_time = dt.date(year, month, day)  + dt.timedelta(1)
    
    context['user_length'] = User.objects.filter(is_active=True).count()
    context['feed_length'] = Message.objects.filter(is_deleted=False).count()
    
    today_start = dt.date(year, month, day)
    today_end = dt.date(year, month, day)  + dt.timedelta(1)
    context['feed_today_length'] = Message.objects.filter(is_deleted=False, reg_date__range=(today_start,today_end)).count()
    context['topic_length'] = Topic.objects.filter(topic_name__gt="").count()
    context['file_length'] = File.objects.filter(is_attached=True).count()
    
    
    context['recent_messages'] = Message.objects.filter(is_deleted=False).order_by("-reg_date")[:5]
    context['recent_users'] = UserLoginHistory.objects.all().order_by("-login_date")[:5]
    return HttpResponse(t.render(context))


def stats_thread(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
        
    t = loader.get_template('admin/stats_thread.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_thread'] = 'selected'
    
    start_date=request.GET.get('start','')
    end_date=request.GET.get('end','')
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    if start_date == '':
        start_date=this_week_start.strftime("%Y-%m-%d")
    if end_date == '':
        end_date=this_week_end.strftime("%Y-%m-%d")
    
    context['start_date']=start_date
    context['end_date']=end_date
    
    start_date=time.strptime(start_date,'%Y-%m-%d')
    start_date=dt.datetime.fromtimestamp(time.mktime(start_date))
    end_date=time.strptime(end_date,'%Y-%m-%d')
    end_date=dt.datetime.fromtimestamp(time.mktime(end_date))
    end_date=end_date+dt.timedelta(1)
    
    #print start_date,end_date
    
    messages = Comment.objects.filter(is_deleted=False,reg_date__range=(start_date,end_date), message__is_deleted=False).values('message').annotate(count = Count('message')).order_by('-count')
    items=list()
    for message in messages:
        feed_id = message['message']
        try:
            feed= Message.objects.get(id=feed_id)
            
            comments = Comment.objects.filter(message=feed,reg_date__range=(start_date,end_date), is_deleted=False)
            feed.comments = comments
            items.append(feed)
        except:
            pass
    
    
    context['items']=items
    return HttpResponse(t.render(context))
    
    
def stats_favorite(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
        
    t = loader.get_template('admin/stats_favorite.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_favorite'] = 'selected'
    
    start_date=request.GET.get('start','')
    end_date=request.GET.get('end','')
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    if start_date == '':
        start_date=this_week_start.strftime("%Y-%m-%d")
    if end_date == '':
        end_date=this_week_end.strftime("%Y-%m-%d")
    
    context['start_date']=start_date
    context['end_date']=end_date
    
    start_date=time.strptime(start_date,'%Y-%m-%d')
    start_date=dt.datetime.fromtimestamp(time.mktime(start_date))
    end_date=time.strptime(end_date,'%Y-%m-%d')
    end_date=dt.datetime.fromtimestamp(time.mktime(end_date))
    end_date=end_date+dt.timedelta(1)
    
    #print start_date,end_date
    
    messages = UserFavorite.objects.filter(reg_date__range=(start_date,end_date), message__is_deleted=False).values('message').annotate(count = Count('message')).order_by('-count')
    items=list()
    for message in messages:
        feed_id = message['message']
        try:
            feed= Message.objects.get(id=feed_id)
            feed.count = message['count']
            comments = Comment.objects.filter(message=feed,reg_date__range=(start_date,end_date), is_deleted=False)
            feed.comments = comments
            items.append(feed)
        except:
            pass
    
    
    context['items']=items
    return HttpResponse(t.render(context)) 
    
    
    
def stats_topic(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()
    
    t = loader.get_template('admin/stats_topic.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_topic'] = 'selected'
    
    context['side_list']=['search_topic']
    my_utils.prepare_search_topic(context)
    
    
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    this_week_end = this_week_end + dt.timedelta(1)
    last_week_start,last_week_end = this_week_start - dt.timedelta(7),this_week_end - dt.timedelta(7)
    
    this_week_topics = Topic.objects.filter(reg_date__range=(this_week_start,this_week_end), topic_name__gt="")
    for topic in this_week_topics:
        try:
            topic.recent_message=''
            recent_message = TopicTimeline.objects.filter(topic=topic).order_by('-update_date')[:1][0]
            topic.recent_message=recent_message.message.contents
        except Exception as e:
            print str(e)
            pass
    context['this_week_topics'] = this_week_topics     
    context['this_week_length'] = Topic.objects.filter(reg_date__range=(this_week_start,this_week_end), topic_name__gt="").count()
    context['last_week_length'] = Topic.objects.filter(reg_date__range=(last_week_start,last_week_end), topic_name__gt="").count()
    if context['last_week_length'] == 0:
        context['increase_rate'] = 100.0
    else:
        context['increase_rate'] = (float(context['this_week_length']) - context['last_week_length'])/context['last_week_length'] * 100
    
    
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
        
        topics = Topic.objects.filter(query_type, topic_name__gt='').order_by('topic_name')
        for topic in topics:
            try:
                topic.recent_message=''
                recent_message = TopicTimeline.objects.filter(topic=topic).order_by('-update_date')[:1][0]
                topic.recent_message=recent_message.message.contents
            except Exception as e:
                print str(e)
                pass
                
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

def get_week_days(year,week):
    d = dt.date(year,1,1)
    if(d.weekday()>3):
        d = d+dt.timedelta(7-d.weekday())
    else:
        d = d - dt.timedelta(d.weekday())
    dlt = dt.timedelta(days = (week-1)*7)
    return d + dlt,  d + dlt + dt.timedelta(days=6)

def stats_member(request):
    if not request.user.is_staff:
        return HttpResponseNotFound()    
    t = loader.get_template('admin/stats_member.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_stats_by_member'] = 'selected'
    context['side_list']=['search_member']
    my_utils.prepare_search_topic(context)
    
    try:
        keyword = request.GET.get('q', '')
        search_index = request.GET.get('index', '')
        query_type = Q()
        if keyword is not '':
            print keyword
            query_type = Q(username__icontains=keyword) | Q(last_name__icontains=keyword)
        
        if search_index is not '':
            if search_index in map(chr, range(65, 91)):
                query_type = Q(username__istartswith=search_index)
            elif search_index == 'number':
                query_type = Q(username__gt="0",username__lt="9")
            else:
                this_index,next_index=my_utils.next_search_index(search_index)
                query_type = Q(username__gt=this_index, username__lt=next_index)
        
        members = User.objects.filter(query_type, is_active=True).order_by('username')
        members_list = list()
        for member in members:
            try:
                member_profile = UserProfile.objects.get(user=member)
                member.profile = member_profile
                try:
                    member.picture = member_profile.picture.url
                except:
                    member.picture = "/media/default.png"
                members_list.append(member)
            except:
                pass
        
        paginator = Paginator(members_list, 5)
        
        page = request.GET.get('page', 1)
        try:
            context['members'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['members'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['members'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['members'].number, paginator.num_pages)
        
    except Exception as e:
        print str(e)
    
    return HttpResponse(t.render(context))
    

def notice(request):
    if not request.user.is_staff:
        return HttpResponseNotFound() 
    t = loader.get_template('admin/notice.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_notice'] = "selected"
    
    return HttpResponse(t.render(context))
    

def send_invites(request):
    if not request.user.is_staff:
        return my_utils.return_error('Invalid')
    
    result=dict()
    result['success']=True
    result['message']='success'
    
    email_list = request.POST.get('email_list',False)
    if not email_list:
        return my_utils.return_error('No list')
    
    try:
        temp_emails = list(set(email_list.split('|')))
        target_emails = list()
        for email in temp_emails:
            if re.match('[\w.]*@\w*\.[\w.]*',email):
                target_emails.append(email)
        print target_emails
        my_emailer.send_invitation_mail(request.user, target_emails)
        
    except Exception as e:
        print str(e)
        return my_utils.return_error('Failed')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def update_notice(request):
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
    
    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
            try: 
                new_notice = Notice(author=user,contents=message,lat=lat,lng=lng,attach_files=attach_list)
                new_notice.save()   
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
    
def delete_notice(request, notice_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            notice = Notice.objects.get(author=user, id=notice_id)
            notice.is_deleted=True
            notice.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
def authority(request):
    if not request.user.is_staff:
        return HttpResponseNotFound() 
    t = loader.get_template('admin/authority.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['side_list']=['']
    context['current_user'] = request.user
    context['page_authority'] = "selected"
    
    try:
        keyword = request.GET.get('q', '')
        search_index = request.GET.get('index', '')
        show_staff = request.GET.get('show_staff','')
        
        query_type = Q()
        if keyword is not '':
            print keyword
            query_type = Q(username__icontains=keyword) | Q(last_name__icontains=keyword)
        
        if search_index is not '':
            if search_index in map(chr, range(65, 91)):
                query_type = Q(username__istartswith=search_index)
            elif search_index == 'number':
                query_type = Q(username__gt="0",username__lt="9")
            else:
                this_index,next_index=my_utils.next_search_index(search_index)
                query_type = Q(username__gt=this_index, username__lt=next_index)
        
        if (keyword is '' and search_index is '') and show_staff == '1':
            context['show_staff']='selected'
            query_type = Q(is_staff=True)
        elif (keyword is '' and search_index is ''):
            context['show_user']='selected'
            query_type = Q(is_staff=False)
        
        members = User.objects.filter(query_type & ~Q(id = request.user.id), is_active=True).order_by('username')
        members_list = list()
        for member in members:
            try:
                member_profile = UserProfile.objects.get(user=member)
                member.profile = member_profile
                try:
                    member.picture = member_profile.picture.url
                except:
                    member.picture = "/media/default.png"
                members_list.append(member)
            except:
                pass
        
        paginator = Paginator(members_list, 10)
        
        page = request.GET.get('page', 1)
        try:
            context['members'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['members'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['members'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['members'].number, paginator.num_pages)
        
    except Exception as e:
        print str(e)
    
    return HttpResponse(t.render(context))   

def authority_update(request):
    if not request.user.is_staff:
        return my_utils.return_error('You don\'t have access.')
    result=dict()
    result['success']=True
    result['message']='success'
    
    user_list = request.POST.get('user_list',False)
    action = request.POST.get('action',False)
    if not user_list:
        return my_utils.return_error('No user.')
    if not action:
        return my_utils.return_error('No Action.')
        
    user_list = user_list.split('|')

    for user_id in user_list:
        if user_id == '':
            continue
        try:
            user = User.objects.get(id=user_id)
            if action == 'user':
                user.is_staff=False
            if action == 'admin':
                user.is_staff=True
            user.save()
        except Exception as e:
            print str(e)
            pass
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')