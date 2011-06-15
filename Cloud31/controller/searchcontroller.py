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


import json

def ajax_user(request):
    result=list()
    q=''
    if request.GET.get('q'):
        q=request.GET['q']
    else:
        return HttpResponse(json.dumps(result, indent=4))
    
    users = User.objects.filter(username__startswith=q)
    
    for user in users:
        item = dict()
        item['caption'] = user.username
        result.append(item)
    
    return HttpResponse(json.dumps(result, indent=4))