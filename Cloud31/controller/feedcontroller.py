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
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode


import json
import parser
import my_utils

@login_required(login_url='/signin/')
def feed(request):
    t = loader.get_template('feed.html')
    context = RequestContext(request)
    context['load_type']='me'
    
    context['side_list']=['user_profile']
    
    user = get_object_or_404(User,username=request.user.username)
    user_profile = get_object_or_404(UserProfile,user=user)
    context['current_user'] = user
    context['user_profile'] = user_profile
    return HttpResponse(t.render(context))
    

def delete_feed(request, feed_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            message = Message.objects.get(author=user, id=feed_id)
            message.is_deleted=True
            message.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    

def delete_comment(request, comment_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            comment = Comment.objects.get(author=user, id=comment_id)
            comment.is_deleted=True
            comment.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    
def load_comany_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        messages = Message.objects.filter(is_deleted=False).order_by('-reg_date')[:5]
        result['feeds']=my_utils.process_messages(request,messages)                
    except:
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4))
    
def load_notice(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        notices = Notice.objects.filter(is_deleted=False).order_by('-reg_date')[:5]
        result['feeds']=my_utils.process_messages(request,notices)                
    except:
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4))



def load_feed(request, user_name):
    if user_name is not '':
        return get_user_feed(request,user_name)
    return my_utils.return_error('user_name is empty')



def load_my_timeline(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            timelines = UserTimeline.objects.filter(user=user,message__is_deleted=False).order_by('-update_date')[:5]
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        messages.append(timeline.message)
                except:
                    pass
            
            result['feeds']=my_utils.process_messages(request,messages)
                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4))   

# def get_my_feed(request):
#     result=dict()
#     result['success']=True
#     result['message']='success'
#     
#     try:
#         user = User.objects.get(username=request.user.username)
#         try:
#             messages = Message.objects.filter(author=user,is_deleted=False).order_by('-reg_date')
#             result['feeds']=my_utils.process_messages(request,messages)
#                 
#         except:
#             result['success']=True
#             result['message']='Do not have any message'
#     except:
#             result['success']=False
#             result['message']='no such user'
#             
#     return HttpResponse(json.dumps(result, indent=4))

def get_user_feed(request,user_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=user_name)
        try:
            messages = Message.objects.filter(author=user,is_deleted=False).order_by('-reg_date')
            result['feeds']=my_utils.process_messages(request,messages)                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4))
    





def update_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    message=''
    attach_list=''
    location_info=''
    if request.method == 'POST':
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['attach_list']:
            attach_list=request.POST['attach_list']
            
        if request.POST['location_info']:
            attach_list=request.POST['location_info']
        
    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
            try: 
                new_message = Message(author=user,contents=message,location=location_info,attach_files=attach_list)
                new_message.save()   
            except:
                return my_utils.return_error('Insert Failed')
                     
            try:
                author_timeline_new = UserTimeline(message=new_message,user=user)
                author_timeline_new.save()
            except:
                return my_utils.return_error('Timelilne Failed')
                
            target_users=parser.detect_users(message)
            target_users=my_utils.remove_duplicates(target_users)
            count = len(target_users)
            for i, user_name in enumerate(target_users):
                try:
                    if user_name != request.user.username:
                        target_user = User.objects.get(username=user_name)
                        target_user_timeline_new = UserTimeline(message=new_message,user=target_user)
                        target_user_timeline_new.save()
                        if i is not (count - 1):
                            new_message.related_users+=user_name+','
                        else:
                            new_message.related_users+=user_name
                except:
                    pass
            
            new_message.save()
            
            #TODO: UPDATE TARTGET_USER TIMELINE & TOPIC TIMELINE
            target_topics=parser.detect_topics(message)
            target_topics=my_utils.remove_duplicates(target_topics)
            count = len(target_topics)
            for i,topic_name in enumerate(target_topics):
                try:
                    topic = Topic.objects.get_or_create(topic_name=topic_name)[0]
                    topic.save()
                    
                    topic_timeline_new = TopicTimeline(message=new_message, topic=topic)
                    topic_timeline_new.save()
                    if i is not (count - 1):
                        new_message.related_topics+=topic_name+','
                    else:
                        new_message.related_topics+=topic_name
                    
                except Exception as e:
                    print str(e)
                    pass
                    
            new_message.save()
        except:
            return my_utils.return_error('No such User')
    else:
        return my_utils.return_error('Empty Message')
    
    return HttpResponse(json.dumps(result, indent=4))


def update_comment(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    input_message=''
    if request.method == 'POST':
        if request.POST['message']:
            input_message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST['feed_id']:
            feed_id = request.POST['feed_id']

    if input_message is not '':
        try:
            user = User.objects.get(username=request.user.username)
        except:
            return my_utils.return_error('Please Sign in first')
        
        try:
            message = Message.objects.filter(id=feed_id,is_deleted=False)[0]
        except:
            return my_utils.return_error('No such Message')
            
        try: 
            new_comment = Comment(author=user,contents=input_message,message=message)
            new_comment.save()
        except:
            return my_utils.return_error('Insert Failed')
        
        #Add To author Timeline
        try:
            author_timeline_new = UserTimeline.objects.filter(message=message,user=user)[0]
        except:
            #현재 없는 경우에만 넣는다.
            try:
                print 'hi'
                author_timeline_new = UserTimeline.objects.get_or_create(message=message,user=user)[0]
                author_timeline_new.save()
            except:
                pass
        
        try:
            related_timelines = UserTimeline.objects.filter(message=message)
            if not related_timelines:
                pass
            for timeline in related_timelines:
                try:
                    if timeline.user.username != request.user.username:
                        print timeline.user.username
                        timeline.save()
                except:
                    pass
        except Exception as e:
            print str(e)
            return my_utils.return_error('Related Timelilne Failed')
            
        #Question! Should do insert into related Topic timeline?
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
    

def load_favorite(request, user_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
        try:
            favorites = UserFavorite.objects.filter(user=user).order_by('-reg_date')
            messages = list()
            for favorite in favorites:
                try:
                    if not favorite.message.is_deleted:
                        messages.append(favorite.message)
                except:
                    pass
            
            result['feeds']=my_utils.process_messages(request,messages)
                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4))
    


def favorite_action(request, feed_id):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        user = User.objects.get(username=request.user.username)
    except:
        return my_utils.return_error('Please Sign in first')
        
    try:
        message = Message.objects.filter(id=feed_id,is_deleted=False)[0]
    except:
        return my_utils.return_error('No such Message')
    
    try:
        user_favorite = UserFavorite.objects.get_or_create(message=message,user=user)[0]
        user_favorite.save()     
    except Exception as e:
        print str(e)
        return my_utils.return_error('Insert Failed')
    
    return HttpResponse(json.dumps(result, indent=4))
    
def unfavorite_action(request, feed_id):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=request.user.username)
    except:
        return my_utils.return_error('Please Sign in first')
        
    try:
        message = Message.objects.filter(id=feed_id,is_deleted=False)[0]
    except:
        return my_utils.return_error('No such Message')
    
    try:
        user_favorite = UserFavorite.objects.filter(message=message,user=user)[0]
        user_favorite.delete()     
    except Exception as e:
        print str(e)
        return my_utils.return_error('Delete Failed')
      
    return HttpResponse(json.dumps(result, indent=4))
