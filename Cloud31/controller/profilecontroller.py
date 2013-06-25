#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *
from controller.settingcontroller import *

from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.encoding import smart_unicode

from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import never_cache

import os,json
from django.conf import settings
from io import BufferedWriter,FileIO

import my_utils
 
@login_required(login_url='/signin/')
def user(request, username):
    t = loader.get_template('profile.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['side_list']=['user_profile']
    my_utils.load_side_profile_info(username, context)
    
    
    return HttpResponse(t.render(context))

@login_required(login_url='/signin/')
def favorite(request):
    t = loader.get_template('favorite.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_favorite']='selected'
    context['side_list']=['user_profile']
    my_utils.load_side_profile_info(request.user.username, context)
    
    return HttpResponse(t.render(context))


def picture(request,username):
    try:
        user = get_object_or_404(User,username=username)
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.picture.name:
            return HttpResponseRedirect(user_profile.picture.name)
    except Exception as e:
        print str(e)
            
    return HttpResponseRedirect('/media/default.png')
    
def picture_size(request,size,username):
    try:
        user = get_object_or_404(User,username=request.user.username)
        user_profile = get_object_or_404(UserProfile,user=user)
        filename = user_profile.picture.name+".thumb.png"
        pathName = os.path.join(settings.MEDIA_ROOT, filename)
        if os.path.isfile(pathName):
            return HttpResponseRedirect("/media/"+filename)
        else:
        	make_thumbnail(user)
        	return HttpResponseRedirect("/media/"+filename)
    except Exception as e:
        print str(e)
            
    return HttpResponseRedirect('/media/default.png')


