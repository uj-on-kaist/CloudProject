#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core import serializers

from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode
from django.db.models import Q

import json
import my_utils
import parser

from datetime import datetime
from django.db.models import Q

from controller.notificationcontroller import *

DEFAULT_LOAD_LENGTH = 3

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('event.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_event'] = "selected"
    context['side_list']=['event_calendar']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    return HttpResponse(t.render(context))
    
@login_required(login_url='/signin/')
def new(request):
    t = loader.get_template('event_new.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_event'] = "selected"
    context['side_list']=['event_calendar']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    return HttpResponse(t.render(context))
    

# Event 하나를 상세히 보여주는 페이지
@login_required(login_url='/signin/')
def detail_event(request, event_id):
    t = loader.get_template('event_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_event'] = "selected"
    context['side_list']=['event_calendar']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return HttpResponse(t.render(context))
    
    query_type = Q(host=user) | Q(invited_users__contains=username) | Q(is_public=True)
    try:
        events = Event.objects.filter(query_type,is_deleted=False,id=event_id)
        context['event']=process_events(events, user)[0]
    except Exception as e:
        print str(e)
        context['error_message'] = 'You cannot access to this event.'
        pass
    
    return HttpResponse(t.render(context))
    


def event_detail(request, event_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return my_utils.return_error('Sign in')
    
    query_type = Q(host=user) | Q(invited_users__contains=username) | Q(is_public=True)
    try:
        events = Event.objects.filter(query_type,is_deleted=False,id=event_id)
        result['event']=process_events(events, user)[0]
    except Exception as e:
        print str(e)
        pass
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def load_event(request, load_type):
    result=dict()
    result['success']=True
    result['message']='success'
    result['events']=list()
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return my_utils.return_error('Sign in')
    query_type = Q(host=user) | Q(invited_users__contains=username) | Q(is_public=True)
    
    if load_type == 'upcoming':
        query_type = (query_type) & Q(start_time__gt = datetime.now())
    elif load_type == 'past':
        query_type = (query_type) & Q(start_time__lte = datetime.now())
    elif load_type == 'me':
        query_type = Q(host=user)
        
    base_id = request.GET.get("base_id",False)
    additional = Q()
    if base_id:
        try:
            event = Event.objects.get(id=base_id)
            additional = Q(reg_date__lt=event.reg_date)
        except:
            pass
    
    try:
        events = Event.objects.filter(query_type,additional,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        result['events']=process_events(events , user)
        
        if len(events) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
                   
    except Exception as e:
        print str(e)
        pass
    
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def attend_event(request, event_id):
    result=dict()
    result['success']=True
    result['message']='success'
    result['events']=list()
    
    if request.method == 'POST':
        if request.POST['attend_type']:
            attend_type=request.POST['attend_type']
    
    if attend_type not in ['yes','no','wait']:
        return my_utils.return_error('Invalid Status')
    
    try:
        user = User.objects.get(username=request.user.username)
        username = request.user.username
        username +=","
    except Exception as e:
        print str(e)
        return my_utils.return_error('Sign in')
    
    query_type = Q(host=user) | Q(invited_users__contains=username) | Q(is_public=True)
    query_type = (query_type) & Q(start_time__gt = datetime.now())
    try:
        event = Event.objects.filter(query_type,is_deleted=False,id=event_id)[0]
    except Exception as e:
        print str(e)
        return my_utils.return_error('Invalid Action')

    try:
        event_attend = EventParticipate.objects.get_or_create(event=event, user=user)[0]
        event_attend.attend_status = attend_type
        event_attend.save()
    except Exception as e:
        print str(e)
        return my_utils.return_error('Insert Failure')
    
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def process_events(events, user):
    results=list()
    for event in events:
        item = dict()
        item['id']=event.id
        item['base_id']=event.id
        item['host']=event.host.username
        item['host_picture']=UserProfile.objects.get(user=event.host).picture.url
        item['host_name']=event.host.last_name
        item['title']= event.title
        item['location']= event.location
        item['attend_open']= (datetime.now() < event.start_time)
        try:
            item['start_time'] = str(event.start_time)
        except:
            pass
        
        try:
            item['end_time'] = str(event.end_time)
        except:
            pass
        item['contents']= parser.parse_text(event.contents)
        item['invited_users']= event.invited_users.replace(",", ", ")
        item['reg_date']= str(event.reg_date)
        item['public']=event.is_public
        item['comments']=list()
        try:
            comments = EventComment.objects.filter(event=event, is_deleted=False).order_by('reg_date')
            for comment in comments:
                c_item = dict()
                c_item['id']=comment.id
                c_item['author']=comment.author.username
                c_item['author_picture']=UserProfile.objects.get(user=comment.author).picture.url
                c_item['author_name']=comment.author.last_name
                c_item['contents']= parser.parse_text(comment.contents)
                c_item['reg_date']= str(comment.reg_date)
                item['comments'].append(c_item)
        except:
            pass
        item['attendees']=list()
        try:
            attendees = EventParticipate.objects.filter(event=event)
            for attendee in attendees:
                a_item=dict()
                a_item['username']=attendee.user.username
                a_item['picture']=UserProfile.objects.get(user=attendee.user).picture.url
                a_item['name']=attendee.user.last_name
                if attendee.attend_status == 'yes':
                    item['attendees'].append(a_item)
                if attendee.user.username == user.username:
                    item['attend_status']=attendee.attend_status
                    print attendee.attend_status
        except:
            pass
            
        try:
            attending = EventParticipate.objects.filter(event=event, user=user)[0]
            item['attending'] = attending.attend_status
        except:
            item['attending'] = 'not yet'
            pass
        results.append(item)
    return results


def register_event(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    title=''
    start_time=''
    end_time=''
    location=''
    invited_text=''
    message=''
    public=False
    
    if request.method == 'POST':
        if request.POST['title']:
            title=smart_unicode(request.POST['title'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['start_time']:
            start_time=request.POST['start_time']
            try:
                start_time=datetime.strptime(start_time,'%Y-%m-%d %I:%M %p')
            except:
                pass
        
        if request.POST['end_time']:
            try:
                end_time=datetime.strptime(request.POST['end_time'],'%Y-%m-%d %I:%M %p')
            except:
                pass

        if request.POST['location']:
            location=smart_unicode(request.POST['location'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['invited_text']:
            invited_text=request.POST['invited_text']
            
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['public']:
            public = False
            if request.POST['public'] == 'true':
                public = True
            print public

    if title is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except Exception as e:
            print str(e)
            return my_utils.return_error('No such User')
            
        try: 
            new_event = Event(host=user,title=title,contents=message, \
                                start_time=start_time, \
                                location=location,is_public=public)
            try:
                if end_time is not '':
                    new_event.end_time = end_time
            except:
                pass
            new_event.save()   
        except Exception as e:
            print str(e)
            return my_utils.return_error('Insert Failed')
               
        target_users=parser.detect_users(invited_text)
        target_users=my_utils.remove_duplicates(target_users)
        count = len(target_users)
        for i, user_name in enumerate(target_users):
            try:
                if user_name != request.user.username:
                    target_user = User.objects.get(username=user_name)
                    new_event.invited_users+=user_name+','
                    
                    print user_name
                    # TODO : ADD EACH USER Notification
                    #SEND NOTIFICATION
                    info = dict()
                    info['from'] = user
                    info['to'] = target_user
                    info['target_object'] = new_event
                    register_noti(request, "new_event_invite",info)
            except:
                pass
            
        new_event.save()

    else:
        return my_utils.return_error('Emtpy Title')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
            
    
    
    
def update_event_comment(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    input_message=''
    if request.method == 'POST':
        if request.POST['message']:
            input_message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST['event_id']:
            event_id = request.POST['event_id']

    if input_message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Please Sign in first')
        
        try:
            event = Event.objects.filter(id=event_id,is_deleted=False)[0]
        except:
            return my_utils.return_error('No such Event')
            
        try: 
            new_comment = EventComment(author=user,contents=input_message,event=event)
            new_comment.save()
        except:
            return my_utils.return_error('Insert Failed')
        
        #TODO: Add To event host & comment authors NOTIFICATION 

    else:
        return my_utils.return_error('Empty Message')
    
    try:
        item = dict()
        item['id']=new_comment.id
        item['author']=new_comment.author.username
        item['author_picture']=UserProfile.objects.get(user=new_comment.author).picture.url
        item['author_name']=new_comment.author.last_name
        item['contents']= parser.parse_text(new_comment.contents)
        item['reg_date']= str(new_comment.reg_date)
        result['comment']=item
    except Exception as e:
        print str(e)
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
    
    
def delete_event(request, event_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            event = Event.objects.get(host=user, id=event_id)
            event.is_deleted=True
            event.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def delete_event_comment(request, comment_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            comment = EventComment.objects.get(author=user, id=comment_id)
            comment.is_deleted=True
            comment.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')