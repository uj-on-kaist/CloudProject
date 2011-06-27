#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.encoding import smart_unicode

from django.contrib.auth.decorators import login_required


import os,json
from django.conf import settings
from io import BufferedWriter,FileIO

import my_utils
 
@login_required(login_url='/signin/')
def user(request, username):
    t = loader.get_template('profile.html')
    context = RequestContext(request)
    
    user = get_object_or_404(User,username=username)
    user_profile = get_object_or_404(UserProfile,user=user)
    target_user = get_object_or_404(UserProfile, user=user)
    
    
    context['side_list']=['user_profile']
    context['target_user']=target_user
    context['user_profile']=user_profile
    
    context['related_topics'] = my_utils.get_related_topics(username)
    context['load_type']='user#'+username
    return HttpResponse(t.render(context))

@login_required(login_url='/signin/')
def favorite(request):
    t = loader.get_template('favorite.html')
    context = RequestContext(request)
    
    user = get_object_or_404(User,username=request.user.username)
    user_profile = get_object_or_404(UserProfile,user=user)
    target_user = get_object_or_404(UserProfile, user=user)
    
    context['page_favorite']='selected'
    context['side_list']=['user_profile']
    context['target_user']=target_user
    context['related_topics'] = my_utils.get_related_topics(request.user.username)
    
    return HttpResponse(t.render(context))

def picture(request,username):
    try:
        user = get_object_or_404(User,username=username)
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.picture.name:
            return HttpResponseRedirect('/media/'+user_profile.picture.name)
    except Exception as e:
        print str(e)
            
    return HttpResponseRedirect('/media/default.png')


