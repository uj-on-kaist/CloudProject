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

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('event.html')
    context = RequestContext(request)
#     user = get_object_or_404(User,username=request.user.username)
    
    context['side_list']=['event_calendar']
    return HttpResponse(t.render(context))
    

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
    try:
        events = Event.objects.filter(query_type,is_deleted=False).order_by('-reg_date')[:5]
        result['events']=process_events(events)                
    except Exception as e:
        print str(e)
        pass
    
    
    return HttpResponse(json.dumps(result, indent=4))

def process_events(events):
    results=list()
    for event in events:
        item = dict()
        item['id']=event.id
        item['host']=event.host.username
        item['host_name']=event.host.last_name
        item['title']= event.title
        item['location']= event.location
        try:
            item['start_time'] = str(event.start_time)
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
                c_item['author_name']=comment.author.last_name
                c_item['contents']= parser.parse_text(comment.contents)
                c_item['reg_date']= str(comment.reg_date)
                item['comments'].append(c_item)
        except:
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

                    # TODO : ADD EACH USER TIMELINE
                    
            except:
                pass
            
        new_event.save()

    else:
        return my_utils.return_error('Emtpy Title')
    
    return HttpResponse(json.dumps(result, indent=4))
            
    
    
    
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
        item['contents']= parser.parse_text(new_comment.contents)
        item['reg_date']= str(new_comment.reg_date)
        result['comment']=item
    except Exception as e:
        print str(e)
    return HttpResponse(json.dumps(result, indent=4))
    
    
    
    
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
            
    return HttpResponse(json.dumps(result, indent=4))
    

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
            
    return HttpResponse(json.dumps(result, indent=4))