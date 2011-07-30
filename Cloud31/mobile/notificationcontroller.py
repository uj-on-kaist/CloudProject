#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *
from controller.forms import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils

from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

def get_notifications(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['unread_notis']=list()
    try:
        user = User.objects.get(username=request.user.username)
        try:
            unread_notis = UserNotification.objects.filter(~Q(notification_type='new_event_invite'),user=user,is_read=False).order_by('-reg_date')
            unread_notis_count = UserNotification.objects.filter(~Q(notification_type='new_event_invite'),user=user, is_read=False).order_by('-reg_date').count()
            read_notis = UserNotification.objects.filter(user=user, is_read=True).order_by('-reg_date')[:10]
            result['unread_notis_count']=unread_notis_count
            
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
            
        if noti.related_type == "Message":
            try:
                feed = Message.objects.filter(id=noti.related_id,is_deleted=False)
                result['feed']=my_utils.process_messages(request,feed)[0]
            except Exception as e:
                print str(e)
                pass
        elif noti.related_type == "DM" or noti.related_type == "DM_Reply":
            try:
                message = DirectMessage.objects.filter(id=noti.related_id,is_deleted=False)
                # result['dm']=my_utils.process_messages(request,message)[0]
            except Exception as e:
                print str(e)
                pass
            
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
            contents_new = noti.contents.replace("<b>","<a>")
            contents_new = contents_new.replace("</b>","</a>")
            item['contents']=contents_new
            item['reg_date']=str(noti.reg_date)
            item['is_read']=noti.is_read
            item['pretty_date'] = my_utils.pretty_date(noti.reg_date)
            try:
                user_profile = UserProfile.objects.get(user=noti.sender)
                item['sender_picture']= user_profile.picture.url
            except:
                item['sender_picture']='/media/default.png'
            
            result.append(item)
        except Exception as e:
            pass
    return result