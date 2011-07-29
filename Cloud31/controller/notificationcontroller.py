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

DEFAULT_LOAD_LENGTH = 10


@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('notifications.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['load_type']='unread'
    context['unread_selected']='selected'
    context['read_selected']=''
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    context['side_list']=['']
    
    
    context['current_user'] = request.user
    context['page_feed'] = "selected"
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    
    print context['user_favorite_topics']
    
    return HttpResponse(t.render(context))
    
@login_required(login_url='/signin/')
def read(request):
    t = loader.get_template('notifications.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    context['load_type']='read'
    context['unread_selected']=''
    context['read_selected']='selected'
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    context['side_list']=['']
    
    
    context['current_user'] = request.user
    context['page_feed'] = "selected"
    context['user_favorite_topics'] = my_utils.get_favorite_topics(request.user)
    
    print context['user_favorite_topics']
    
    return HttpResponse(t.render(context))


@never_cache
def get_notifications(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['unread_notis']=list()
    try:
        user = User.objects.get(username=request.user.username)
        try:
            unread_notis = UserNotification.objects.filter(user=user, is_read=False).order_by('-reg_date')[:5]
            
            read_notis = UserNotification.objects.filter(user=user, is_read=True).order_by('-reg_date')[:5]
            result['unread_notis']=process_notis(request,unread_notis)
            result['read_notis']=process_notis(request,read_notis)
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Invalid action'
            
    except:
            return my_utils.return_error('Please Sign in First')
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
@never_cache
def get_typed_notifications(request, typed):
    result=dict()
    result['success']=True
    result['message']='success'
    result['notis']=list()
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        user = User.objects.get(username=request.user.username)
        try:
            if typed == 'unread':
                unread_notis = UserNotification.objects.filter(additional,user=user,is_read=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
                result['notis']=process_notis(request,unread_notis)
            
                if len(unread_notis) == DEFAULT_LOAD_LENGTH:
                    result['load_more']=True
            else:
                read_notis = UserNotification.objects.filter(additional,user=user,is_read=True).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
                result['notis']=process_notis(request,read_notis)
            
                if len(read_notis) == DEFAULT_LOAD_LENGTH:
                    result['load_more']=True
            
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Invalid action'
            
    except:
            return my_utils.return_error('Please Sign in First')
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def read_notification(request, noti_id):
    result=dict()
    result['success']=True
    result['message']='success'
    result['notifications']=list()
    try:
        user = User.objects.get(username=request.user.username)
        try:
            noti = UserNotification.objects.filter(user=user, id=noti_id)[0]
            noti.is_read=True
            noti.save()
        except Exception as e:
            print str(e)
            return my_utils.return_error('Invalid action')
            
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def process_notis(request, notis):
    result=list()
    for noti in notis:
        try:
            item = dict()
            item['id']=noti.id
            item['base_id']=noti.id
            item['receiver']=noti.user.username
            item['sender']=noti.sender.username
            item['noti_type']=noti.notification_type
            item['related_type']=noti.related_type
            item['related_id']=noti.related_id
            item['contents']=noti.contents
            item['reg_date']=str(noti.reg_date)
            item['is_read']=noti.is_read
            
            try:
                user_profile = UserProfile.objects.get(user=noti.sender)
                item['sender_picture']= user_profile.picture.url
            except:
                item['sender_picture']='/media/default.png'
            
            result.append(item)
        except Exception as e:
            pass
    return result
    
    
import re
def register_noti(request, noti_type, info):
    try:        
        target_user = info['to']
        sender = info['from']
        target_object = info['target_object']
        if noti_type == 'new_comment':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            target_message=smart_unicode(target_message, encoding='ascii', strings_only=False, errors='strict')
            contents = u"<b>"+sender.username+u"</b>님께서 메시지 <b>"+target_message+u"</b>에 새 댓글을 다셨습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="Message", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save()
        elif noti_type == 'new_at_feed':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            target_message=smart_unicode(target_message, encoding='ascii', strings_only=False, errors='strict')
            contents = u"<b>"+sender.username+u"</b>님께서 회원님에 관한 메시지 <b>"+target_message+u"</b>를 작성하셨습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="Message", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save()
        elif noti_type == 'new_event_invite':
            contents = u"<b>"+sender.username+u"</b>님께서 회원님을 이벤트 <b>"+target_object.title+u"</b>에 초대하셨습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="Event", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save() 
        elif noti_type == 'new_dm':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            target_message=smart_unicode(target_message, encoding='ascii', strings_only=False, errors='strict')
            contents = u"<b>"+sender.username+u"</b>님께서 회원님에게 쪽지 <b>"+target_message+u"</b>를 보냈습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="DM", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save()
        elif noti_type == 'new_dm_reply':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            target_message=smart_unicode(target_message, encoding='ascii', strings_only=False, errors='strict')
            contents = u"<b>"+sender.username+u"</b>님께서 회원님에게 쪽지 <b>"+target_message+u"</b>에 답장을 작성하셨습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="DM_Reply", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save()
        
        
        #TODO : EMAIL NOTI - User Option Check
        
        #TODO : iPhone Notification
        if not new_noti:
            return
        try:
            register_iPhone_notification(new_noti, noti_type, info)
        except Exception as e:
            print str(e)
            
    except Exception as e:
        print 'Error '+str(e)
        pass

def register_iPhone_notification(noti, noti_type, info):
    print 'iPhone Noti'
    target_user = noti.user
    sender = noti.sender
    try:
        target_user_profile = UserProfile.objects.get(user=target_user)
    except:
        return
    
    if target_user_profile.device_id == "":
        return

    try:
        notification_type='iphone'
        target_object = info['target_object']
        print info
        if noti_type == 'new_comment':
            target_message = target_object.contents
            target_message = target_message[:20] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            contents = sender.username+u"님께서 메시지 \""+target_message+u"\"에 새 댓글을 다셨습니다."
            new_noti = NotificationQueue(target_user=target_user, notification_type=notification_type, contents = contents)
            new_noti.save()
        elif noti_type == 'new_at_feed':
            target_message = target_object.contents
            target_message = target_message[:20] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            contents = sender.username+u"님께서 회원님에 관한 메시지 \""+target_message+u"\"를 작성하셨습니다."
            new_noti = NotificationQueue(target_user=target_user, notification_type=notification_type, contents = contents)
            new_noti.save()
        elif noti_type == 'new_event_invite':
            contents = sender.username+u"님께서 회원님을 이벤트 \""+target_object.title+u"\"에 초대하셨습니다."
            new_noti = NotificationQueue(target_user=target_user, notification_type=notification_type, contents = contents)
            new_noti.save() 
        elif noti_type == 'new_dm':
            target_message = target_object.contents
            target_message = target_message[:20] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            contents = sender.username+u"님께서 회원님에게 쪽지 \""+target_message+u"\"를 보냈습니다."
            new_noti = NotificationQueue(target_user=target_user, notification_type=notification_type, contents = contents)
            new_noti.save()
        elif noti_type == 'new_dm_reply':
            target_message = target_object.contents
            target_message = target_message[:20] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            contents = sender.username+u"님께서 회원님에게 쪽지 \""+target_message+u"\"에 답장을 작성하셨습니다."
            new_noti = NotificationQueue(target_user=target_user, notification_type=notification_type, contents = contents)
            new_noti.save()
            
    except Exception as e:
        print 'Error '+str(e)
        pass
    
    
    
    