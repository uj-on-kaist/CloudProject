#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.utils.encoding import smart_unicode

from controller.models import *

from django.template import Context, loader

import datetime,json
from hashlib import sha1


from django.conf import settings


def encode(string) : 
    return sha1(string).hexdigest()
    
def send_activation_mail(user,user_profile):
    shaSource= user.username + user.email
    activation_key=encode(shaSource)
    key_expires = datetime.datetime.today() + datetime.timedelta(2)
    
    user_profile.activation_key=activation_key
    user_profile.key_expires=key_expires
    user_profile.save()
    
    t = loader.get_template('email/activation.html')
    context = Context()
    context['activation_link'] = 'http://localhost:8000/confirm/?key='+activation_key
    email_body = t.render(context)
    email_subject = smart_unicode('Cloud31 계정 인증을 완료해 주세요!', encoding='utf-8', strings_only=False, errors='strict')
    
    register_email_queue(user.email, email_subject, email_body)


def send_invitation_mail(from_user, target_emails):
    t = loader.get_template('email/invitation.html')
    context = Context()
    context['from_user'] = from_user.username
    context['from_user_name'] = from_user.last_name
    context['SERVICE_BASE_URL'] = settings.SERVICE_BASE_URL
    email_body = t.render(context)
    email_subject = smart_unicode('Cloud31를 사용해 보세요!', encoding='utf-8', strings_only=False, errors='strict')
    
    for email in target_emails:
        register_email_queue(email, email_subject, email_body)
    

def register_email_queue(target_email,subject,contents):
    try:
        if target_email != '' and target_email is not None:
            email = EmailQueue(target_email=target_email,subject=subject, contents=contents)
            email.save()
    except Exception as e:
        print str(e)
        pass