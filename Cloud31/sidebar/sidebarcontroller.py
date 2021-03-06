#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *
from sidebar.models import *
from django.utils.encoding import smart_unicode
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.db.models import Q

from django.contrib.auth.decorators import login_required


import json, re
from controller import my_utils
from controller import parser

from controller import my_emailer

DEFAULT_LOAD_LENGTH = 5

def load_poll(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['dialogs']=list()
    if not request.user:
        return my_utils.return_error('Please Sign in First')
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        polls = Poll.objects.filter(additional,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        
        polls_list = list()
        for poll in polls:
            poll_item = dict()
            poll_item['id'] = poll.id
            poll_item['title'] = poll.title
            poll_item['author'] = poll.author.username
            poll_item['author_name'] = poll.author.last_name
            poll_item['reg_date'] = str(poll.reg_date)
            polls_list.append(poll_item)
        
        result['polls']=polls_list
        
        if len(polls_list) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
        
    except Exception as e:
        print str(e)
        return my_utils.return_error('Internal Error')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    

def load_dialog(request):
    result=dict()
    result['success']=True
    result['message']='success'
    result['dialogs']=list()
    if not request.user:
        return my_utils.return_error('Please Sign in First')
    
    try:
        base_id = request.GET.get("base_id",False)
        additional = Q()
        if base_id:
            additional = Q(id__lt=base_id)
        
        dialogs = Dialog.objects.filter(additional,is_deleted=False).order_by('-reg_date')[:DEFAULT_LOAD_LENGTH]
        result['dialogs']=process_dialogs(dialogs)
        
        if len(dialogs) == DEFAULT_LOAD_LENGTH:
            result['load_more']=True
        
    except Exception as e:
        print str(e)
        return my_utils.return_error('Internal Error')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')

def add_dialog(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    dialog=request.POST.get('dialog',False)
    if not dialog:
        return my_utils.return_error('Invalid Access')
    
    dialog=smart_unicode(dialog, encoding='utf-8', strings_only=False, errors='strict')
    
    try:
        user = User.objects.get(username=request.user.username)
    except:
        return my_utils.return_error('Sign in first')
    
    try: 
        new_dialog = Dialog(author=user,contents=dialog)
        new_dialog.save()
        dialog = Dialog.objects.get(id=new_dialog.id)
        result['dialog']=process_dialogs([dialog])[0]
    except:
        return my_utils.return_error('Send Message Failure')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def delete_dialog(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    if request.method != "POST" or not request.user:
        return my_utils.return_error('Invalid Access')
    
    dialog_id = request.POST.get('dialog_id',False)
    if not dialog_id:
        return my_utils.return_error('Invalid ID')
    try:
        user = User.objects.get(username=request.user.username)
        try:
            dialog = Dialog.objects.get(author=user, id=dialog_id)
            dialog.is_deleted=True
            dialog.save()
        except:
            result['success']=True
            result['message']='Invalid action'
    except:
            return my_utils.return_error('Please Sign in First')
    
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
    

def process_dialogs(dialogs):
    result=list()
    for dialog in dialogs:
        try:
            item = dict()
            item['id']=dialog.id
            item['user']=dialog.author.username
            item['username']=dialog.author.last_name
            item['contents']=parser.parse_text(dialog.contents)
            item['reg_date']=str(dialog.reg_date)
            result.append(item)
        except:
            pass
    return result
    
    
    
    
def send_invite(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    emails = request.GET.get('emails',False)
    
    if emails:
        try:
            temp_emails = list(set(emails.split('|')))
            target_emails = list()
            for email in temp_emails:
                if re.match('[\w.]*@\w*\.[\w.]*',email):
                    target_emails.append(email)
            print target_emails
            my_emailer.send_invitation_mail(request.user, target_emails)
        except:
            pass
        
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')