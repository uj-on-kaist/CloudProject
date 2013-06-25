#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode

from django.db.models import Q

import json
import my_utils

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

DEFAULT_LOAD_LENGTH = 10

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('location.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['side_list']=['']
    context['page_location'] = "selected"
    
    return HttpResponse(t.render(context))
    
    
def get_random_feeds(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    try:
        feeds = Message.objects.filter(~Q(lat='') & ~Q(lng=''), is_deleted=False).order_by('?').order_by('-id')[:DEFAULT_LOAD_LENGTH]
        
        result['feeds']=my_utils.process_messages(request,feeds)
    except Exception as e:
        print str(e)
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')
    
def get_location_feeds(request):
    result=dict()
    result['success']=True
    result['message']='success'
    
    sw = request.GET.get('sw',False)
    ne = request.GET.get('ne',False)
    if not sw or not ne:
        return my_utils.return_error('No GPS')
    
    try:
        sw_lat, sw_lng = sw.split(",")
        ne_lat, ne_lng = ne.split(",")
    except Exception as e:
        print str(e)
        return my_utils.return_error('GPS Error')
        
    
    try:
        base_id = request.GET.get('base_id',False)
        additional = Q()
        if base_id:
            additional = Q(id__lt = base_id)
        feeds = Message.objects.filter(additional, lat__range=(sw_lat,ne_lat),lng__range=(sw_lng,ne_lng), is_deleted=False).order_by('-id')[:DEFAULT_LOAD_LENGTH]
        if len(feeds) == DEFAULT_LOAD_LENGTH:
                result['load_more']=True
        
        result['feeds']=my_utils.process_messages(request,feeds)
    except Exception as e:
        print str(e)
        return my_utils.return_error('Error')
    return HttpResponse(json.dumps(result, indent=4), mimetype='application/json')