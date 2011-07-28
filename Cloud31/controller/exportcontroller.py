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
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_unicode

from django.db.models import Q

import json
import parser
import my_utils


from controller.notificationcontroller import *

from pyofc2  import * 
import random
import time

from datetime import datetime
import datetime as dt
from django.db.models import Q

from django.db.models import Count

import random

from tempfile import TemporaryFile
from xlwt import Workbook

from controller.admincontroller import *

def process_test(request):
    start_date=request.GET.get('start','')
    end_date=request.GET.get('end','')
    
    now = dt.datetime.now().isocalendar()
    this_week_start,this_week_end = get_week_days(now[0],now[1])
    if start_date == '':
        start_date=this_week_start.strftime("%Y-%m-%d")
    if end_date == '':
        end_date=this_week_end.strftime("%Y-%m-%d")
    
    start_date=time.strptime(start_date,'%Y-%m-%d')
    start_date=dt.datetime.fromtimestamp(time.mktime(start_date))
    end_date=time.strptime(end_date,'%Y-%m-%d')
    end_date=dt.datetime.fromtimestamp(time.mktime(end_date))
    end_date=end_date+dt.timedelta(1)
    
    wb = Workbook()
    ws = wb.add_sheet('Sheetname')
    ws.write(0, 0, 'Firstname')
    ws.write(0, 1, 'Surname')
    ws.write(1, 0, 'Hans')
    ws.write(1, 1, 'Muster')

    fname = 'process_excel-testfile.xls'
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    wb.save(response)

    return response