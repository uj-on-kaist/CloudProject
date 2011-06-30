#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.utils.encoding import smart_unicode

from controller.models import *

from django.template import Context, loader

import datetime,json
from hashlib import sha1





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
    
    register_email_queue(user, email_subject, email_body)


def register_email_queue(user,subject,contents):
    try:
        email = EmailQueue(target_user=user,subject=subject, contents=contents)
        email.save()
    except Exception as e:
        print str(e)
        pass