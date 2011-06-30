from django_cron import cronScheduler, Job

from django.core.mail import send_mail

from controller.models import *
from controller.forms import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from django.core.mail import EmailMultiAlternatives

class Send_Email_Worker(Job):
    run_every = 3
    def job(self):
        print '[Cron: Send_Email_Worker]'
        emails = EmailQueue.objects.filter(is_sent=False)
        print emails
        if len(emails) is not 0:
            print '[Cron: Send_Email_Worker] Start Emailing'
            for email in emails:
                try:
                    receiver = email.target_user.email
                    
                    msg = EmailMultiAlternatives(email.subject, '', 'Cloud31<hr95jung@naver.com>', [receiver])
                    msg.attach_alternative(email.contents, "text/html")
                    msg.send()
                    
                    email.is_sent=True
                    email.save()
                except Exception as e:
                    print str(e)
            print '[Cron: Send_Email_Worker] Finish Emailing'

cronScheduler.register(Send_Email_Worker)




"""
from django_cron import cronScheduler, Job

                
class Send_Email_Worker(Job):
    run_every = 3            
    def job(self):
        print '[Cron: Send_Email_Worker] Start'
        print '[Cron: Send_Email_Worker] End'


cronScheduler.register(Send_Email_Worker)
"""