#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.utils.encoding import smart_unicode


import re
def parse_text(text):
    text=smart_unicode(text, encoding='utf-8', strings_only=False, errors='strict')
    items=text.split(" ")
    new_items = []
    for item in items:
        prefix = item[:1]
        link_prefix = item[:7]
        if prefix == "#":
            item_text = item[1:]
            item = '<a class="detect_item" href="/topic/'+item_text+'">'+prefix+'<span>'+item_text+'</span></a>'
            
        if prefix == "@":
            item_text=re.sub("\W","",item)
            item_remain=item[1:].replace(item_text,'')
            item = '<a class="detect_item" href="/user/'+item_text+'">'+prefix+'<span>'+item_text+'</span></a>'+item_remain
        
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
            item_text=re.sub("\W","",item)
            detected_users.append(item_text)
     
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