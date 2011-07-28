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
from django.utils.encoding import smart_unicode

from django.db.models import Q

import json
import my_utils

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from operator import itemgetter

DEFAULT_LOAD_LENGTH = 10

@login_required(login_url='/signin/')
def topic(request):
    t = loader.get_template('topic.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    
    context['side_list']=['search_topic']
    my_utils.prepare_search_topic(context)
    
    context['page_topic'] = "selected"
    context['topics']=list()
    
    context['popular_topics'] = Topic.objects.filter(reference_count__gt=0,topic_name__gt='').order_by("-reference_count")[:20]
    # try:
#         topics = 
#     except:
#         pass
    
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
        
        topics = Topic.objects.filter(query_type, topic_name__gt='',reference_count__gt=0).order_by('topic_name')
        
        
        paginator = Paginator(topics, 15)
        
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
    
    
@login_required(login_url='/signin/')
def topic_detail(request,topic_id):
    t = loader.get_template('topic_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    print context['user_favorite_topics']
    context['side_list']=['topic_detail']
    context['topic']=list()
    context['topic'] = get_object_or_404(Topic,id=int(topic_id))
    
    
    context['page_topic'] = "selected"
    context['load_type']='topic#' + str(context['topic'].id)
    context['topic_name']=context['topic'].topic_name
    context['topic_id']=context['topic'].id
    
    context['topic_favorited']=False
    for favorite in context['user_favorite_topics']:
        if context['topic_id'] == favorite['id']:
            context['topic_favorited']=True
    
    context['related_users']=my_utils.get_related_users(context['topic'].topic_name)
    return HttpResponse(t.render(context))
    
    
def load_topic_timeline(request,topic_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        topic = Topic.objects.get(id=topic_id)
        try:
            timelines = TopicTimeline.objects.filter(additional, topic=topic).order_by('-update_date')[:DEFAULT_LOAD_LENGTH]
            if not timelines:
                result['feeds']=my_utils.process_messages(request, list())
                return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        timeline.message.base_id=timeline.id
                        messages.append(timeline.message)
                except:
                    pass
            
            if len(timelines) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
            
            result['feeds']=my_utils.process_messages(request, messages)
                
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such Topic')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    


def update_description(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    topic_id = request.POST.get('topic_id',False)
    new_description = request.POST.get('desc',False)
    new_description = smart_unicode(new_description, encoding='utf-8', strings_only=False, errors='strict')

    try:
        topic = Topic.objects.get(id=topic_id)
        topic.topic_detail = new_description
        topic.save()
    except Exception as e:
        print str(e)
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
    
def topic_favorite(request, topic_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
    except:
        return my_utils.return_error('Please Sign in first')
        
    try:
        topic = Topic.objects.filter(id=topic_id)[0]
        result['topic_name']=topic.topic_name
    except:
        return my_utils.return_error('No such Topic')
    
    try:
        user_topic_favorite = UserTopicFavorite.objects.get_or_create(topic=topic,user=user)[0]
        user_topic_favorite.save()     
    except Exception as e:
        print str(e)
        return my_utils.return_error('Insert Failed')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def topic_unfavorite(request, topic_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
    except:
        return my_utils.return_error('Please Sign in first')
        
    try:
        topic = Topic.objects.filter(id=topic_id)[0]
    except:
        return my_utils.return_error('No such Topic')
    
    try:
        user_topic_favorite = UserTopicFavorite.objects.filter(topic=topic,user=user)[0]
        user_topic_favorite.delete()     
    except Exception as e:
        print str(e)
        return my_utils.return_error('Delete Failed')
      
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    