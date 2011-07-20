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
from controller.notificationcontroller import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils
from controller import parser

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update(request):
    result=dict()
    result['success']=True
    result['message']='success'
    message=''
    attach_list=''
    location_info=''
    lat = ''
    lng = ''
    if request.method == 'POST':
        if request.POST.get('message',False):
            message=smart_unicode(request.POST['message'], encoding='utf-8', strings_only=False, errors='strict')
        if request.POST.get('attach_list',False):
            attach_list=request.POST['attach_list']
        if request.POST.get('location_info',False):
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
        except Exception as e:
            return my_utils.return_error('No such User')
    else:
        return my_utils.return_error('Empty Message')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')