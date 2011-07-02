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


import json
import parser
import my_utils

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
            item['receiver']=noti.user.username
            item['sender']=noti.sender.username
            item['noti_type']=noti.notification_type
            item['related_type']=noti.related_type
            item['related_id']=noti.related_id
            item['contents']=noti.contents
            item['reg_date']=str(noti.reg_date)
            item['is_read']=noti.is_read
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
        print info
        if noti_type == 'new_comment':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            p = re.compile(r'<.*?>')
            target_message = p.sub('', target_message)
            print target_message
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
            print target_message
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
            print target_message
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
        
    except Exception as e:
        print 'Error '+str(e)
        pass
    
    
    
    