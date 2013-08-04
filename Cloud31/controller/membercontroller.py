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

@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('member.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['side_list']=['search_member']
    context['page_member'] = "selected"
    my_utils.prepare_search_topic(context)
    
    try:
        keyword = request.GET.get('q', '')
        search_index = request.GET.get('index', '')
        query_type = Q()
        if keyword is not '':
            print keyword
            query_type = Q(username__icontains=keyword) | Q(last_name__icontains=keyword)
        
        if search_index is not '':
            if search_index in map(chr, range(65, 91)):
                query_type = Q(username__istartswith=search_index)
            elif search_index == 'number':
                query_type = Q(username__gt="0",username__lt="9")
            else:
                this_index,next_index=my_utils.next_search_index(search_index)
                query_type = Q(username__gt=this_index, username__lt=next_index)
        
        members = User.objects.filter(query_type, is_active=True).order_by('username')
        members_list = list()
        for member in members:
            try:
                member_profile = UserProfile.objects.get(user=member)
                member.profile = member_profile
                try:
                    member.picture = my_utils.get_user_thumbnail(member)
                except:
                    member.picture = "/media/default.png"
                if not member_profile.is_deactivated:
                    members_list.append(member)
            except:
                pass
        
        paginator = Paginator(members_list, 15)
        
        page = request.GET.get('page', 1)
        try:
            context['members'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['members'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['members'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['members'].number, paginator.num_pages)
        
    except Exception as e:
        print str(e)
        
    
    
    return HttpResponse(t.render(context))