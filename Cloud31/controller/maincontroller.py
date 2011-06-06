#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

def main(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/feed/')
    
    return HttpResponseRedirect('/signin/')