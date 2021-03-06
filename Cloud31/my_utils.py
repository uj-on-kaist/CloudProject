#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from controller.models import *
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode
from django.http import HttpResponse

import json
import parser
import re

from django.conf import settings

def load_basic_info(request, context):
    user_profile = get_object_or_404(UserProfile,user=request.user)
    context['user_profile'] = user_profile
       
    try:
        context['user_favorite_topics']=get_favorite_topics(request.user)
    except:
        pass

def load_side_profile_info(username, context):
    user = get_object_or_404(User,username=username)
    user_profile = get_object_or_404(UserProfile,user=user)
    target_user = get_object_or_404(UserProfile, user=user)
    
    context['target_user']=target_user
    context['target_user_profile']=user_profile
    context['related_topics'] = get_related_topics(username)
    context['load_type']='user#'+username

def get_favorite_topics(user):
    result=list()
    try:
        favorites = UserTopicFavorite.objects.filter(user=user)
        for favorite in favorites:
            result.append(favorite.topic.topic_name)
    except Exception as e:
        print 'Error '+str(e)
        pass
    return result

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
        try:
            user_profile = UserProfile.objects.get(user=message.author)
            feed['author_picture']= user_profile.picture.url
        except:
            feed['author_picture']='/media/default.png'
        feed['author_name']=message.author.last_name
        feed['contents']= parser.parse_text(message.contents)
        feed['location']= message.location
        feed['reg_date']= str(message.reg_date)
        feed['comments'] = list()
        feed['file_list'] = list()
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
                try:
                    user_profile = UserProfile.objects.get(user=comment.author)
                    item['author_picture']= user_profile.picture.url
                except:
                    item['author_picture']='/media/default.png'
                item['contents']= parser.parse_text(comment.contents)
                item['reg_date']= str(comment.reg_date)
                feed['comments'].append(item)
        except:
            pass
        
        attach_files = message.attach_files.split('.')
        if attach_files[0] is not u'':
            try:
                files = File.objects.filter(id__in=attach_files)
                feed['file_list']=process_files(files)
            except Exception as e:
                print str(e)
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
    
import os.path

def process_files(files):
    result = list()
    for a_file in files:
        try:
            item = dict()
            #file_path = settings.PROJECT_PATH + '/media/'+smart_unicode(a_file.file_contents.url, encoding='utf-8', strings_only=False, errors='strict')
            #if not os.path.isfile(file_path):
            #    print file_path
            #    print 'not file'
            item['type']=a_file.file_type
            item['uploader']=a_file.uploader.username
            item['upload_date']=str(a_file.upload_date)
            if a_file.file_type.lower() in ['xls','xlsx']:
                item['type']='excel'
                item['type_name']='Excel file'
            elif a_file.file_type.lower() in ['doc','docx']:
                item['type']='word'
                item['type_name']='Word file'
            elif a_file.file_type.lower() in ['ppt','pptx']:
                item['type']='ppt'
                item['type_name']='Powerpoint file'
            elif a_file.file_type.lower() in ['ppt','pptx']:
                item['type']='ppt'
                item['type_name']='Powerpoint file'
            elif a_file.file_type.lower() in ['hwp']:
                item['type_name']='HWP file'
            elif a_file.file_type.lower() in ['pdf']:
                item['type_name']='PDF file'
            elif a_file.file_type.lower() in ['zip']:
                item['type_name']='Zip file'
            elif a_file.file_type.lower() in ['png', 'jpg', 'jpeg', 'gif']:
                item['type']='img'
                item['type_name']='Image file'
            else:
                item['type']='etc'
                item['type_name']='Unknown type' 
            item['name']=smart_unicode(a_file.file_name, encoding='utf-8', strings_only=False, errors='strict')
            item['url']=a_file.file_contents.url
            result.append(item)
        except Exception as e:
            print str(e)
            pass
    return result  


def remove_duplicates(input_list):
    return list(set(input_list))
    
    
def return_error(msg):
    print msg
    result=dict()
    result['success']=False
    result['message']=msg
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')




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
    


def get_index_list(index, last_index):
    result = dict()
    result['index_list']=list()
    result['current_index']=index
    left = int((index-1)/10)*10 + 1
    right = min(left+10, last_index+1)
    
    result['has_previous'] = False
    if left > 1:
        result['has_previous']=True
        result['previous_index']=left-1
    
    for i in range(left,right):
        result['index_list'].append(i)
    
    result['has_next']=False
    if right < last_index+1:
        result['has_next']=True
        result['next_index']=right
    
    
    return result

HANGUL_BEGIN_UNICODE = 44032
HANGUL_BASE_UNIT = 588

def next_search_index(index):
    ko = [u'ㄱ',u'ㄲ',u'ㄴ',u'ㄷ',u'ㄸ',u'ㄹ',u'ㅁ',u'ㅂ',u'ㅃ',u'ㅅ',u'ㅆ',u'ㅇ',u'ㅈ',u'ㅉ',u'ㅊ',u'ㅋ',u'ㅌ',u'ㅍ',u'ㅎ']
     
    try:
        uni_index = ko.index(index)
        this_index = unichr(HANGUL_BEGIN_UNICODE+uni_index*HANGUL_BASE_UNIT)
        next_index = unichr(HANGUL_BEGIN_UNICODE+(uni_index+1)*HANGUL_BASE_UNIT)
        return this_index, next_index
    except:
        pass
        
        

def get_related_users(topic_name):
    print 123123
    try:
        users = Message.objects.filter(related_topics__contains=topic_name+',').values('author').distinct()[:20]
        result = list()
        for author in users:
            user_id = int(author['author'])
            try:
                user = User.objects.filter(id=user_id, is_active=True)[0]
                result.append(user.username)
            except Exception as e:
                print str(e)
                pass
            
        return result
    except Exception as e:
        print str(e)
        return list()    
    
    
def prepare_search_topic(context):
    context['ko_list']=[u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ', u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ']
    context['en_list']=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']