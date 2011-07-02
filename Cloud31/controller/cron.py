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

#TODO : iPhone Noti sender

#TODO : SQL Backup