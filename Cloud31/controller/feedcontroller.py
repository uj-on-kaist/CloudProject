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
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode

from django.db.models import Q

import json
import parser
import my_utils


from controller.notificationcontroller import *


DEFAULT_LOAD_LENGTH = 20

@login_required(login_url='/signin/')
def feed(request):
    t = loader.get_template('feed.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['load_type']='me'
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    context['side_list']=['']
    
    
    context['current_user'] = request.user
    context['page_feed'] = "selected"
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    return HttpResponse(t.render(context))


@login_required(login_url='/signin/')
def feed_detail(request, feed_id):
    t = loader.get_template('feed_detail.html')
    context = RequestContext(request)
    
    user = get_object_or_404(User,username=request.user.username)
    user_profile = get_object_or_404(UserProfile,user=user)
    
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    context['current_user'] = user
    context['page_feed'] = "selected"
    context['user_profile'] = user_profile
    
    feed = get_object_or_404(Message,id=feed_id)
    if not feed.is_deleted:
        feed = my_utils.process_messages(request, [feed])
        context['feed'] = feed[0]
    
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
            
            try:
                related_topics = message.related_topics.split(",")
                for topic_name in related_topics:
                    if topic_name:
                        topic = Topic.objects.get(topic_name=topic_name)
                        topic.reference_count -=1
                        topic.save()
                
                related_topic_timelines = TopicTimeline.objects.filter(message=message)
                for timeline in related_topic_timelines:
                    timeline.delete()
            
            except Exception as e:
                print str(e)+"[11234]"
                pass
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

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
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

@never_cache
def load_comany_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        base_id = request.GET.get("base_id",False)
        to_id = request.GET.get("to_id",False)
        sort_method = request.GET.get("sort","reg_date")
        additional = Q()
        load_length = DEFAULT_LOAD_LENGTH
        if base_id:
            try:
                if sort_method == 'reg_date':
                    message = Message.objects.get(id=base_id)
                    additional = Q(reg_date__lt=message.reg_date)
                else:
                    message = Message.objects.get(id=base_id)
                    additional = Q(update_date__lt=message.update_date)
            except:
                pass
            #additional = Q(id__lt=base_id)
        if to_id:
            load_length = 10000
            additional = Q(id__gte=base_id)
        
        
        if sort_method == 'reg_date':
            messages = Message.objects.filter(additional,is_deleted=False).order_by('-reg_date')[:load_length]
        else:
            messages = Message.objects.filter(additional,is_deleted=False).order_by('-update_date')[:load_length]
        
        
        result['feeds']=my_utils.process_messages(request,messages)
        
        if len(messages) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
    except Exception as e:
        print str(e)
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

@never_cache
def load_notice(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        notices = Notice.objects.filter(additional,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        result['feeds']=my_utils.process_messages(request,notices)
        
        if len(notices) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True             
    except:
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


@never_cache
def load_feed(request, user_name):
    if user_name is not '':
        return get_user_feed(request,user_name)
    return my_utils.return_error('user_name is empty')


@never_cache
def load_my_timeline(request):
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        user = User.objects.get(username=request.user.username)
        try:
            base_id = request.GET.get("base_id",False)
            to_id = request.GET.get("to_id",False)
            sort_method = request.GET.get("sort","reg_date")
            additional = Q()
            load_length=DEFAULT_LOAD_LENGTH
            if base_id:
                try:
                    if sort_method == 'reg_date':
                        timeline = UserTimeline.objects.get(id=base_id)
                        additional = Q(message__reg_date__lt=timeline.message.reg_date)
                    else:
                        timeline = UserTimeline.objects.get(id=base_id)
                        additional = Q(message__update_date__lt=timeline.message.update_date)
                except:
                    pass
            if to_id:
                try:
                    timeline = UserTimeline.objects.get(id=base_id)
                    additional = Q(update_date__gte=timeline.update_date)
                except:
                    pass               
            
            
            if sort_method == 'reg_date':
                timelines = UserTimeline.objects.filter(additional,user=user,message__is_deleted=False).order_by('-message__reg_date')[:load_length]
            else:
                timelines = UserTimeline.objects.filter(additional,user=user,message__is_deleted=False).order_by('-message__update_date')[:load_length]
            
            if len(timelines) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
            messages = list()
            for timeline in timelines:
                try:
                    if not timeline.message.is_deleted:
                        timeline.message.base_id=timeline.id
                        messages.append(timeline.message)
                except:
                    pass
            
            result['feeds']=my_utils.process_messages(request,messages)
                
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')   

def get_user_feed(request,user_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=user_name)
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        try:
            messages = Message.objects.filter(additional, author=user,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
            result['feeds']=my_utils.process_messages(request,messages)
            
            if len(messages) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
            
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def get_user_at_feed(request,user_name):
    if user_name is '':
        return my_utils.return_error('user_name is empty')
    result=dict()
    result['success']=True
    result['message']='success'
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        messages = Message.objects.filter(additional, related_users__contains=user_name+',',is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        result['feeds']=my_utils.process_messages(request,messages)
        
        if len(messages) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True             
    except:
        result['success']=True
        result['message']='Do not have any message'
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def load_favorite(request, user_name):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        user = User.objects.get(username=user_name)
        try:
            base_id = request.GET.get("base_id",False)
            additional = Q()
            if base_id:
                additional = Q(id__lt=base_id)
            
            favorites = UserFavorite.objects.filter(additional, user=user,message__is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
            messages = list()
            
            for favorite in favorites:
                try:
                    if not favorite.message.is_deleted:
                        favorite.message.base_id=favorite.id
                        messages.append(favorite.message)
                except Exception as e:
                    print str(e)
                    pass
            
            if len(favorites) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
            
            result['feeds']=my_utils.process_messages(request,messages)
                
        except:
            result['success']=True
            result['message']='Do not have any message'
    except:
            return my_utils.return_error('No Such User')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    


def update_feed(request):
    result=dict()
    result['success']=True
    result['message']='success'
    message=''
    attach_list=''
    location_info=''
    lat = ''
    lng = ''
    if request.method == 'POST':
        if request.POST['message']:
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        
        if request.POST['attach_list']:
            attach_list=request.POST['attach_list']
            
        if request.POST['location_info']:
            location_info=request.POST['location_info']
            try:
                location = location_info.split("|")
                lat = location[0]
                lng = location[1]
            except:
                pass
    
    if message is not '':
        try:
            user = User.objects.get(username=request.user.username)
            print location_info
            try: 
                new_message = Message(author=user,contents=message,lat=lat,lng=lng,attach_files=attach_list)
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
                        new_message.related_users+=user_name+','
                        
                        #SEND NOTIFICATION
                        info = dict()
                        info['from'] = user
                        info['to'] = target_user
                        info['target_object'] = new_message
                        register_noti(request, "new_at_feed",info)
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
                    topic.reference_count +=1
                    topic.save()
                    
                    topic_timeline_new = TopicTimeline(message=new_message, topic=topic)
                    topic_timeline_new.save()
                    
                    new_message.related_topics+=topic_name+','
                except Exception as e:
                    print "QWER: "+str(e)
                    pass
                    
            new_message.save()
            
            
            #FILE CHECK
            attach_arr = attach_list.split('.')
            for attach_id in attach_arr:
                try:
                    if attach_id is '':
                        continue
                    attach = File.objects.get(id=attach_id)
                    attach.is_attached=True
                    attach.save()
                except Exception as e:
                    print str(e)
        except:
            return my_utils.return_error('No such User')
    else:
        return my_utils.return_error('Empty Message')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')


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
            message.save()
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
                        timeline.save()
                        
                        #SEND NOTIFICATION
                        info = dict()
                        info['from'] = request.user
                        info['to'] = timeline.user
                        info['comment'] = input_message
                        info['target_object'] = message
                        register_noti(request, "new_comment",info)
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
        #item['author_picture']=UserProfile.objects.get(user=new_comment.author).picture.url
        item['author_picture']=my_utils.get_user_thumbnail(new_comment.author)
        item['author_name']=new_comment.author.last_name
        item['contents']= parser.parse_text(new_comment.contents)
        item['reg_date']= str(new_comment.reg_date)
        result['comment']=item
    except Exception as e:
        print str(e)
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    


    


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
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
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
      
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
