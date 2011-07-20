#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.mail import send_mail

from controller.models import *
from controller.forms import *
from controller.notificationcontroller import *

import datetime,json

from django.utils.encoding import smart_unicode

from django.conf import settings

from controller import my_emailer
from controller import my_utils
from controller import parser

from django.views.decorators.csrf import csrf_exempt


from django import forms 

class ImageUploadForm(forms.Form):
    fileExtension = forms.CharField()
    picture = forms.FileField()
import uuid
from django.core.files.base import ContentFile
@csrf_exempt
def file_upload(request):
    result = dict()
    result['code'] = 0
    result['success'] = True
    try:
        if request.method == 'POST':
            user=User.objects.get(id=request.user.id)
            if user:
                file_content = ContentFile(request.FILES['photo'].read())
                fileExtension=request.POST.get('fileExtension','')
                file_name=request.FILES['photo'].name
                new_file = File(file_type=fileExtension,file_name=file_name, uploader=user)
                fileName2 = user.username + "_" + str(uuid.uuid1()) +'.'+ fileExtension
                new_file.file_contents.save(request.FILES['photo'].name, file_content)
                new_file.save()
                result['file_id']=new_file.id
            else:
                return my_utils.return_error('No User')
    except Exception as e:
        print str(e)
        return my_utils.return_error('Empty Message')
    return HttpResponse(json.dumps(result))