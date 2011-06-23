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
            query_type = query_type & Q(contents__contains=item)
        feeds = Message.objects.filter(query_type, is_deleted=False)
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
            query_type = query_type & Q(topic_name__contains=item)
        topics = Topic.objects.filter(query_type)
        for topic in topics:
            item = dict()
            item['name']=topic.topic_name
            item['detail']=topic.topic_detail
            result.append(item)
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
            query_type = query_type & Q(file_name__contains=item)
        files = File.objects.filter(query_type)
        for a_file in files:
            item = dict()
            item['type']=a_file.file_type
            if a_file.file_type in ['xls','xlsx']:
                item['type']='excel'
                item['type_name']='Excel file'
            elif a_file.file_type in ['doc','docx']:
                item['type']='word'
                item['type_name']='Word file'
            elif a_file.file_type in ['ppt','pptx']:
                item['type']='ppt'
                item['type_name']='Powerpoint file'
            elif a_file.file_type in ['ppt','pptx']:
                item['type']='ppt'
                item['type_name']='Powerpoint file'
            elif a_file.file_type in ['hwp']:
                item['type_name']='HWP file'
            elif a_file.file_type in ['pdf']:
                item['type_name']='PDF file'
            elif a_file.file_type in ['zip']:
                item['type_name']='Zip file'
            else:
                item['type']='etc'
                item['type_name']='Unknown type' 
            item['name']=a_file.file_name
            item['url']='/media/'+a_file.file_contents.url
            result.append(item)
    except Exception as e:
        print str(e)
        pass
    return result

def search_locations(request, inStr):
    result = list()
    return result

def search_members(request, inStr):
    result = list()
    return result

def ajax_user(request):
    result=dict()
    result['success']=True
    result['items']=list()
    q=''
    if request.GET.get('q'):
        q=request.GET['q']
    else:
        return HttpResponse(json.dumps(result, indent=4))
    
    users = User.objects.filter(username__startswith=q)
    
    for user in users:
        try:
            item = dict()
            item['username'] = user.username
            item['name'] = user.last_name
            user_profile = UserProfile.objects.get(user=user)
            result['items'].append(item)
        except:
            pass
    return HttpResponse(json.dumps(result, indent=4))
    
    
def ajax_topic(request):
    result=dict()
    result['success']=True
    result['items']=list()
    q=''
    if request.GET.get('q'):
        q=request.GET['q']
        q=smart_unicode(request.GET['q'], encoding='utf-8', strings_only=False, errors='strict')
    else:
        return HttpResponse(json.dumps(result, indent=4))
    
    topics = Topic.objects.filter(topic_name__startswith=q)
    
    for topic in topics:
        try:
            item = dict()
            item['topic_name'] = topic.topic_name
            result['items'].append(item)
        except:
            pass
    return HttpResponse(json.dumps(result, indent=4))