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
def setting(request):
    t = loader.get_template('setting.html')
    context = RequestContext(request)
    context['page_setting'] = "selected"
#     user = get_object_or_404(User,username=request.user.username)

    return HttpResponse(t.render(context))