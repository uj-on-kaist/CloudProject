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
def main(request):
    t = loader.get_template('message.html')
    context = RequestContext(request)
    context['current_user']=request.user.username
#     user = get_object_or_404(User,username=request.user.username)

    return HttpResponse(t.render(context))