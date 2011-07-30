#!/usr/bin/python
# -*- coding: utf-8 -*-

from django_cron import cronScheduler, Job

from django.core.mail import send_mail

from controller.models import *
from controller.forms import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.conf import settings


from APNSWrapper import *
from django.conf import settings
import binascii

from django.db.models import Q

#TODO : iPhone Noti sender
class iPhone_APNS_Worker(Job):
    run_every = 3
    def job(self):
        notis = NotificationQueue.objects.filter(is_sent=False)
        if len(notis) is not 0:
            print '[Cron: iPhone_APNS_Worker] Start APNS'
            for noti in notis:
                try:
                    noti.is_sent=True
                    noti.save()
                    target_user = noti.target_user
                    try:
                        target_user_profile = UserProfile.objects.get(user=target_user)
                    except:
                        continue
                    
                    if target_user_profile.device_id == "":
                        continue
                        
                    unread_count = UserNotification.objects.filter(~Q(notification_type='new_event_invite'),user=target_user,is_read=False).count()
                    deviceToken = binascii.unhexlify(target_user_profile.device_id)
                    wrapper = APNSNotificationWrapper(settings.IPHONE_PEM_PATH, True)
                    message = APNSNotification()
                    message.token(deviceToken)
                    message.alert(noti.contents.encode('utf-8'))
                    message.badge(unread_count)
                    message.sound()
                    wrapper.append(message)
                    wrapper.notify()
                    
                except Exception as e:
                    print str(e)
            print '[Cron: iPhone_APNS_Worker] Finish APNS'
            

cronScheduler.register(iPhone_APNS_Worker)


class Send_Email_Worker(Job):
    run_every = 3
    def job(self):
        emails = EmailQueue.objects.filter(is_sent=False)
        if len(emails) is not 0:
            print '[Cron: Send_Email_Worker] Start Emailing'
            for email in emails:
                try:
                    receiver = email.target_email
                    from_user = 'Cloud31<'+settings.EMAIL_HOST_USER+'>'
                    msg = EmailMultiAlternatives(email.subject, '', from_user, [receiver])
                    msg.attach_alternative(email.contents, "text/html")
                    msg.send()
                    
                    email.is_sent=True
                    email.save()
                except Exception as e:
                    print str(e)
            print '[Cron: Send_Email_Worker] Finish Emailing'

cronScheduler.register(Send_Email_Worker)




#TODO : User 통계(1주일)


#TODO : SQL Backup