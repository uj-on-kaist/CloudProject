#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.utils.encoding import smart_unicode

from controller.models import *

import re
def parse_text(text):
    text=smart_unicode(text, encoding='utf-8', strings_only=False, errors='strict')
    items=text.split(" ")
    new_items = []
    for item in items:
        prefix = item[:1]
        link_prefix = item[:7]
        if prefix == "#":
            topic_name = item[1:]
            topic_name = smart_unicode(topic_name, encoding='utf-8', strings_only=False, errors='strict')
            try:
                topic = Topic.objects.get(topic_name=topic_name, topic_name__gt='')
                item_link=str(topic.id)
                item_text = topic.topic_name
                item = '<a class="detect_item" href="/topic/'+item_link+'">'+prefix+'<span>'+item_text+'</span></a>'
            except Exception as e:
                pass
            
        if prefix == "@":
            item_text=item[1:]
            user_name = smart_unicode(item[1:], encoding='utf-8', strings_only=False, errors='strict')
            try:
                user = User.objects.get(username=user_name)
                item = '<a class="detect_item" href="/user/'+user.username+'">@<span>'+item_text+'</span></a>'
            except:
                pass
            try:
                user = User.objects.get(last_name=user_name)
                item = '<a class="detect_item" href="/user/'+user.username+'">@<span>'+item_text+'</span></a>'
            except:
                pass
        
        if link_prefix == "http://":
            item = '<a href="'+item+'" target=_blank>'+item+'</a>'
            
        new_items.append(item)
            
    result = ""
    for item in new_items:
        result += item + " "
    
    return result.strip()
    

def detect_users(text):
    text=smart_unicode(text, encoding='utf-8', strings_only=False, errors='strict')
    items=text.split(" ")
    detected_users = list()
    for item in items:
        prefix = item[:1]
        if prefix == "@":
            user_name=item[1:]
            try:
                user = User.objects.get(username=user_name)
                detected_users.append(user.username)
                continue
            except:
                pass
            try:
                user = User.objects.get(last_name=user_name)
                detected_users.append(user.username)
                continue
            except:
                pass            
            
     
    return detected_users

def detect_topics(text):
    text=smart_unicode(text, encoding='utf-8', strings_only=False, errors='strict')
    items=text.split(" ")
    detected_topics = list()
    for item in items:
       prefix = item[:1]
       if prefix == "#":
           detected_topics.append(item[1:])
           
    return detected_topics