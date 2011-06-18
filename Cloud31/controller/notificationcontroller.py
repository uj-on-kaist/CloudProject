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
            notis = UserNotification.objects.filter(user=user, is_read=False)[:5]
        except:
            result['success']=True
            result['message']='Invalid action'
            result['notifications']=process_notis(request,notis)
    except:
            return my_utils.return_error('Please Sign in First')
            
    return HttpResponse(json.dumps(result, indent=4))
    
    
    
def process_notis(request, notis):
    result=list()
    for noti in notis:
        try:
            item = dict()
            item['receiver']=notis.user.username
            item['sender']=notis.sender.username
            item['noti_type']=notis.notification_type
            item['related_type']=notis.related_type
            item['related_id']=notis.related_id
            item['contents']=parser.parse_text(notis.contents)
            item['reg_date']=notis.reg_date
            result.append(item)
        except:
            pass
    return result
    
    
    
    
    