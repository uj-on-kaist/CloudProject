#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core import serializers

from django.contrib.auth.decorators import login_required


@login_required(login_url='/signin/')
def user(request, username):
    t = loader.get_template('profile.html')
    context = RequestContext(request)
    
    user = get_object_or_404(User,username=username)
    target_user = get_object_or_404(UserProfile, user=user)
    context['target_user']=target_user
    
    context['load_type']='user#'+username
    return HttpResponse(t.render(context))
    
    
def picture(request,username):
    return HttpResponseRedirect('/media/default.png')