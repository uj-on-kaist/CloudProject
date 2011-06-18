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

def get_notifications(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['notifications']=list()
    try:
        user = User.objects.get(username=request.user.username)
        try:
            notis = UserNotification.objects.filter(user=user).order_by('-reg_date')[:5]
            result['notifications']=process_notis(request,notis)
        except Exception as e:
            print str(e)
            result['success']=True
            result['message']='Invalid action'
            
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    
    
    
def process_notis(request, notis):
    result=list()
    for noti in notis:
        try:
            item = dict()
            item['receiver']=noti.user.username
            item['sender']=noti.sender.username
            item['noti_type']=noti.notification_type
            item['related_type']=noti.related_type
            item['related_id']=noti.related_id
            item['contents']=parser.parse_text(noti.contents)
            item['reg_date']=str(noti.reg_date)
            result.append(item)
        except Exception as e:
            pass
    return result
    
    
    
def register_noti(request, noti_type, info):
    try:        
        target_user = info['to']
        sender = info['from']
        target_object = info['target_object']
        print info
        if noti_type == 'new_comment':
            target_message = target_object.contents
            target_message = target_message[:10] + "..."
            target_message=smart_unicode(target_message, encoding='ascii', strings_only=False, errors='strict')
            contents = u"<b>"+sender.username+u"</b>님께서 메시지 <b>"+target_message+u"</b>에 새 댓글을 다셨습니다."
            new_noti = UserNotification(user=target_user, sender=sender, \
                                        notification_type=noti_type, related_type="Comment", \
                                        related_id = target_object.id, contents = contents)
            new_noti.save()
        
    except Exception as e:
        print 'Error '+str(e)
        pass
    
    
    
    