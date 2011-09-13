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
import datetime as dt
from django.db.models import Q

from controller.notificationcontroller import *

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


DEFAULT_LOAD_LENGTH = 10

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('poll.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_poll'] = "selected"
    context['side_list']=['']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    
    try:
        polls = Poll.objects.filter(is_deleted=False).order_by('reg_date')
        polls_list = list()
        for poll in polls:
            try:
                member_profile = UserProfile.objects.get(user=poll.author)
                try:
                    poll.author.picture = member_profile.picture.url
                except:
                    poll.author.picture = "/media/default.png"
                polls_list.append(poll)
            except:
                pass
        
        paginator = Paginator(polls_list, 15)
        
        page = request.GET.get('page', 1)
        try:
            context['polls'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['members'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['polls'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['polls'].number, paginator.num_pages)
        
    except Exception as e:
        print str(e)
    
    return HttpResponse(t.render(context))

# Poll 하나를 상세히 보여주는 페이지
@login_required(login_url='/signin/')
def detail_poll(request, poll_id):
    t = loader.get_template('poll_detail.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_poll'] = "selected"
    context['side_list']=['']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    
    try:
        poll = Poll.objects.filter(is_deleted=False,id=poll_id)[0]
        try:
            member_profile = UserProfile.objects.get(user=poll.author)
            poll.author.profile = member_profile
            try:
                poll.author.picture = member_profile.picture.url
            except:
                poll.author.picture = "/media/default.png"
        except:
            pass
        
        try:
            comments = PollComment.objects.filter(poll=poll, is_deleted=False).order_by('reg_date')
            for comment in comments:
                author_profile = UserProfile.objects.get(user=comment.author)
                try:
                    comment.author_picture = author_profile.picture.url
                except:
                    comment.author_picture = "/media/default.png"
            poll.comments = comments
        except:
            pass
        
        try:
            options = PollItem.objects.filter(poll=poll)
            for option in options:
                try:
                    option.value = PollAnswer.objects.filter(answer=option).count()
                except:
                    pass
                try:
                    option_answered = PollAnswer.objects.filter(answer=option, answerer=request.user).count()
                    if option_answered:
                        option.checked = True
                    else:
                        option.checked = False
                except:
                    pass
            poll.options = options
        except:
            pass
        
        context['poll'] = poll
    except Exception as e:
        print str(e)
        pass
    
    return HttpResponse(t.render(context))


@login_required(login_url='/signin/')
def new(request):
    t = loader.get_template('poll_new.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_poll'] = "selected"
    context['side_list']=['']
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    return HttpResponse(t.render(context))


def check_option(request, option_info):
    result=dict()
    result['success']=True
    result['message']='success'
    
    option_info = option_info.split("/") 
    option_id = option_info[0]
    option_value = option_info[1]
    
    try:
        poll_option = PollItem.objects.get(id=option_id)
        poll_answer = PollAnswer.objects.get_or_create(answer=poll_option,answerer=request.user)[0]
        if option_value == "1":
            poll_answer.save()
        elif option_value == "0":
            poll_answer.delete()
        result['checked']=option_value
    except Exception as e:
        print str(e)
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def register_poll(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    title=''
    detail=''
    option_count=''
    public=False
    
    if request.method == 'POST':
        if request.POST['title']:
            title=smart_unicode(request.POST['title'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['detail']:
            detail=smart_unicode(request.POST['detail'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['option_count']:
            option_count=request.POST['option_count']
        
        option_list = list()
        
        for i in range(0, int(option_count)):
            try:
                order = 'option'+str(i)
                if request.POST[order]:
                    option_text = smart_unicode(request.POST[order], encoding='utf-8', strings_only=False, errors='strict')
                    option_list.append(option_text)
            except Exception as e:
                print str(e)
                
    
    if title is not '' and len(option_list) is not 0:
        try:
            user = User.objects.get(username=request.user.username)
        except Exception as e:
            print str(e)
            return my_utils.return_error('No such User')
            
        try: 
            new_poll = Poll(author=user,title=title,contents=detail)
            new_poll.save()   
        except Exception as e:
            print str(e)
            return my_utils.return_error('Insert Failed')
            
        for option in option_list:
            try:
                new_poll_item = PollItem(poll=new_poll,detail=option)
                new_poll_item.save()
            except Exception as e:
                print str(e)
                return my_utils.return_error('Insert Failed')

    else:
        return my_utils.return_error('Emtpy Title')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    
def update_poll_comment(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    input_message=''
    if request.method == 'POST':
        if request.POST['message']:
            input_message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST['poll_id']:
            poll_id = request.POST['poll_id']

    if input_message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Please Sign in first')
        
        try:
            poll = Poll.objects.filter(id=poll_id,is_deleted=False)[0]
        except:
            return my_utils.return_error('No such Poll')
            
        try: 
            new_comment = PollComment(author=user,contents=input_message,poll=poll)
            new_comment.save()
        except:
            return my_utils.return_error('Insert Failed')
        
        #TODO: Add To poll author & comment authors NOTIFICATION 

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
    
    
def delete_poll(request, poll_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            poll = Poll.objects.get(author=user, id=poll_id)
            poll.is_deleted=True
            poll.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def delete_poll_comment(request, comment_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            comment = PollComment.objects.get(author=user, id=comment_id)
            comment.is_deleted=True
            comment.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')