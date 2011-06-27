#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from controller.models import *

from django.utils.encoding import smart_unicode
from django.http import HttpResponse

import json
import parser
import re

def remove_special(inStr):
    result = inStr
    result=smart_unicode(result, encoding='utf-8', strings_only=False, errors='strict')
    # try:
#         result=smart_unicode(inStr, encoding='ascii', strings_only=False, errors='strict')
#         result = re.sub('[^가-힣0-9a-zA-Z\\s]', '', result)
#         print result+'/'+inStr
#     except Exception as e:
#         print str(e)
    return result

def process_messages(request, messages):
    feeds=list()
    for message in messages:
        feed = dict()
        feed['id']=message.id
        feed['author']=message.author.username
        feed['author_name']=message.author.last_name
        feed['contents']= parser.parse_text(message.contents)
        feed['attach_files']= message.attach_files
        feed['location']= message.location
        feed['reg_date']= str(message.reg_date)
        feed['comments'] = list()
        
        try:
            feed['base_id']=message.base_id
        except:
            feed['base_id']=message.id
        
        try:
            comments = Comment.objects.filter(message=message, is_deleted=False).order_by('reg_date')
            for comment in comments:
                item = dict()
                item['id']=comment.id
                item['author']=comment.author.username
                item['author_name']=comment.author.last_name
                item['contents']= parser.parse_text(comment.contents)
                item['reg_date']= str(comment.reg_date)
                feed['comments'].append(item)
        except:
            pass
            
        try:
            user = User.objects.get(username=request.user.username)
            is_favorited = UserFavorite.objects.filter(message=message, user=user)[0]
            feed['favorite']=True
        except:
            feed['favorite']=False        
            pass
        feeds.append(feed)
    return feeds
    
    


def remove_duplicates(input_list):
    return list(set(input_list))
    
    
def return_error(msg):
    print msg
    result=dict()
    result['success']=False
    result['message']=msg
    return HttpResponse(json.dumps(result, indent=4))




def get_related_topics(username):
    result = list()
    
    try:
        user = User.objects.get(username=username)
    except:
        return result
    
    
    try:
        messages = Message.objects.filter(author=user)
        topic_list = ''
        for message in messages:
            if message.related_topics != '':
                topic_list += message.related_topics
                
        result = filter(None,list(set(topic_list.split(','))))
    except Exception as e:
        print str(e)
        pass

    return result
    
    


