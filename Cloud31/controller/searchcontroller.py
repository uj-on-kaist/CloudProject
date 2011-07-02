#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *
from django.utils.encoding import smart_unicode
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.db.models import Q

from django.contrib.auth.decorators import login_required


import json
import my_utils

def main(request, keyword):
    t = loader.get_template('search.html')
    context = RequestContext(request)
    keyword=my_utils.remove_special(keyword)
    context['keyword']=keyword
    
    if keyword != '':
        context['feeds']=search_feeds(request, keyword)
        context['topics']=search_topics(request, keyword)
        context['files']=search_files(request, keyword)
        context['locations']=search_locations(request, keyword)
        context['members']=search_members(request, keyword)
        context['keyword'] = keyword
        context['search_length']=len(context['feeds'])+len(context['topics']) \
                            +len(context['files'])+len(context['locations'])+len(context['members'])
    else:
        context['feeds']=list()
        context['topics']=list()
        context['files']=list()
        context['locations']=list()
        context['members']=list()
        context['search_length'] = 0
    return HttpResponse(t.render(context))

def search_feeds(request, inStr):
    result = list()
    
    try:
        arr = inStr.split(' ')
        query_type = Q()
        for item in arr:
            query_type = query_type & Q(contents__icontains=item)
        feeds = Message.objects.filter(query_type, is_deleted=False).order_by('-reg_date')
        result = my_utils.process_messages(request,feeds)
    except Exception as e:
        print str(e)
        pass
    
    return result
    
def search_topics(request, inStr):
    result = list()
    try:
        arr = inStr.split(' ')
        query_type = Q()
        for item in arr:
            query_type = query_type & Q(topic_name__icontains=item)
        topics = Topic.objects.filter(query_type)
        result = topics
    except Exception as e:
        print str(e)
        pass
    return result

def search_files(request, inStr):
    result = list()
    try:
        arr = inStr.split(' ')
        query_type = Q()
        for item in arr:
            query_type = query_type & Q(file_name__icontains=item)
        files = File.objects.filter(query_type, is_attached=True)
        result = my_utils.process_files(files)
    except Exception as e:
        print str(e)
        pass
    return result

def search_locations(request, inStr):
    result = list()
    return result

def search_members(request, inStr):
    result = list()
    try:
        arr = inStr.split(' ')
        query_type_1 = Q()
        query_type_2 = Q()
        for item in arr:
            query_type_1 = query_type_1 & Q(username__icontains=item)
        for item in arr:
            query_type_2 = query_type_2 & Q(last_name__icontains=item)
        members = User.objects.filter(query_type_1 | query_type_2)
        members_list = list()
        for member in members:
            try:
                member_profile = UserProfile.objects.get(user=member)
                member.profile = member_profile
                members_list.append(member)
            except:
                pass
                
        result = members_list
    except Exception as e:
        print str(e)
        pass
    return result

def ajax_user(request):
    result=dict()
    result['success']=True
    result['items']=list()
    q=''
    if request.GET.get('q'):
        q=request.GET['q']
    else:
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    users = User.objects.filter(Q(username__istartswith=q) | Q(last_name__icontains=q))[:15]
    
    for user in users:
        try:
            item = dict()
            item['username'] = user.username
            item['name'] = user.last_name
            user_profile = UserProfile.objects.get(user=user)
            result['items'].append(item)
        except:
            pass
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
def ajax_topic(request):
    result=dict()
    result['success']=True
    result['items']=list()
    q=''
    if request.GET.get('q'):
        q=request.GET['q']
        q=smart_unicode(request.GET['q'], encoding='utf-8', strings_only=False, errors='strict')
    else:
        return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    topics = Topic.objects.filter(topic_name__istartswith=q)
    
    for topic in topics:
        try:
            item = dict()
            item['topic_name'] = topic.topic_name
            result['items'].append(item)
        except:
            pass
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')