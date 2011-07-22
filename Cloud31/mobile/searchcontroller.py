#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *
from controller.forms import *
from controller.notificationcontroller import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils
from controller import parser

from django.views.decorators.csrf import csrf_exempt


DEFAULT_LOAD_LENGTH = 50

def feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['items']=list()
    inStr = request.GET.get('q','')
    if inStr == '' or inStr.strip() == '':
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    base_id = request.GET.get("base_id",False)
    
    try:
        arr = inStr.split(' ')
        query_type = Q()
        additional= Q()
        if base_id:
            additional = Q(id__lt=base_id)
        for item in arr:
            query_type = query_type & Q(contents__icontains=item)
        feeds = Message.objects.filter(query_type, is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        for feed in feeds:
            try:
                user_profile = UserProfile.objects.get(user=feed.author)
                feed.author_picture=user_profile.picture.url
            except Exception as e:
                feed.author_picture='/media/default.png'
        result['items'] = my_utils.process_messages(request,feeds)
        if len(feeds) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
    except Exception as e:
        print str(e)
        pass
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def topic(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['items']=list()
    inStr = request.GET.get('q','')
    if inStr == '' or inStr.strip() == '':
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    base_id = request.GET.get("base_id",False)
    
    try:
        arr = inStr.split(' ')
        query_type = Q()
        additional= Q()
        if base_id:
            additional = Q(id__gt=base_id)
        for item in arr:
            query_type = query_type & Q(topic_name__icontains=item)
        topics = Topic.objects.filter(additional,query_type)[:DEFAULT_LOAD_LENGTH]
        topic_list=list()
        if len(topics) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True        
        for topic in topics:
            a_topic = dict()
            a_topic['result_type']='topic'
            a_topic['topic_name']=topic.topic_name
            a_topic['id']=topic.id
            a_topic['base_id']=topic.id
            topic_list.append(a_topic)
        
        result['items'] = topic_list
    except Exception as e:
        print str(e)
        pass
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def search_file(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['items']=list()
    inStr = request.GET.get('q','')
    inStr=smart_unicode(inStr, encoding='utf-8', strings_only=False, errors='strict')
    if inStr == '' or inStr.strip() == '':
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    base_id = request.GET.get("base_id",False)
    try:
        arr = inStr.split(' ')
        query_type = Q()
        additional= Q()
        if base_id:
            additional = Q(id__gt=base_id)
        for item in arr:
            query_type = query_type & Q(file_name__icontains=item)
        files = File.objects.filter(additional,query_type, is_attached=True)[:DEFAULT_LOAD_LENGTH]
        if len(files) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True        
        result['items']=my_utils.process_files(files)
    except Exception as e:
        print str(e)
        pass
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')   
    
def member(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['items']=list()
    inStr = request.GET.get('q','')
    if inStr == '' or inStr.strip() == '':
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    base_id = request.GET.get("base_id",False)
    try:
        arr = inStr.split(' ')
        query_type_1 = Q()
        query_type_2 = Q()
        additional= Q()
        if base_id:
            additional = Q(id__gt=base_id)
        for item in arr:
            query_type_1 = query_type_1 & Q(username__icontains=item)
        for item in arr:
            query_type_2 = query_type_2 & Q(last_name__icontains=item)
        
        members = User.objects.filter(additional,query_type_1 | query_type_2, is_active=True)[:DEFAULT_LOAD_LENGTH]
        if len(members) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
        members_list = list()
        for member in members:
            a_member=dict()
            try:
                member_profile = UserProfile.objects.get(user=member)
                a_member['result_type']='member'
                a_member['userID']=member.username
                a_member['name']=member.last_name
                a_member['dept']=member_profile.dept
                a_member['position']=member_profile.position
                a_member['base_id']=member.id
                try:
                    a_member['picture'] = member_profile.picture.url
                except:
                    a_member['picture'] = "/media/default.png"
                members_list.append(a_member)
            except:
                pass
                
        result['items'] = members_list
    except Exception as e:
        print str(e)
        pass
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')