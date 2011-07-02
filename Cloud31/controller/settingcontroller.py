#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.http import HttpResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from controller.models import *

from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.encoding import smart_unicode

from django.contrib.auth.decorators import login_required


import os,json
from django.conf import settings
from io import BufferedWriter,FileIO

import my_utils

@login_required(login_url='/signin/')
def setting(request):
    t = loader.get_template('setting.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['page_setting'] = "selected"
    user = get_object_or_404(User,username=request.user.username)
    user_profile = get_object_or_404(UserProfile,user=user)
    context['user'] = user
    context['user_profile'] = user_profile
    context['user_picture_url'] = '/media/default.png'
    if user_profile.picture:
        context['user_picture_url']=user_profile.picture.url
    return HttpResponse(t.render(context))



import re
def update(request, update_type):
    t = loader.get_template('setting.html')
    context = RequestContext(request)
    context['page_setting'] = "selected"
    
    if request.method != "POST":
        return HttpResponse1Redirect("/setting")
    
    user = get_object_or_404(User,username=request.user.username)
    user_profile = get_object_or_404(UserProfile,user=user)
    
    if update_type == 'account':
        new_email = request.POST.get("new_email",False)
        if new_email != '':
            if re.match('[\w.]*@\w*\.[\w.]*',new_email):
                try:
                    user.email=new_email
                    user.save()
                except:
                    context['email_error_msg']="Error occured."
                    context['email_error_input']=new_email
                    pass
            else:
                context['email_error_msg']="Invalid Email Address."
                context['email_error_input']=new_email
        
        new_password = request.POST.get("new_password",False)
        password1 = request.POST.get("password1",False)
        password2 = request.POST.get("password2",False)
        
        if (new_password != '') and (password1 != '') and (password2 != ''):
            length_valid= True
            #length_valid=len(password) >= 6
            equal_valid = (password1 == password2)
            
            check_valid = user.check_password(password1)
            if length_valid and equal_valid and check_valid:
                user.set_password(new_password)
                user.save()
            else:
                if not length_valid:
                    context['password_error_msg']="Please input more than 6 characters."
                else:
                    context['password_error_msg']="Password does not match."
    
    
    if update_type == 'profile':
        new_last_name = request.POST.get("new_last_name",False)
        if new_last_name != '':
            user.last_name = smart_unicode(new_last_name, encoding='utf-8', strings_only=False, errors='strict')
            user.save()
        
        new_dept = request.POST.get("new_dept",False)
        if new_dept != '':
            user_profile.dept = smart_unicode(new_dept, encoding='utf-8', strings_only=False, errors='strict')
            user_profile.save()
        
        new_position = request.POST.get("new_position",False)
        if new_position != '':
            user_profile.position = smart_unicode(new_position, encoding='utf-8', strings_only=False, errors='strict')
            user_profile.save()
        
      
    context['user'] = user
    context['user_profile'] = user_profile
    return HttpResponse(t.render(context))








    

from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.core.files.base import ContentFile
@csrf_exempt
def ajax_upload( request ):
    if not request.user.is_authenticated():
        return HttpResponse('Login')
    if request.method == "POST":
        # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
        if request.is_ajax( ):
            # the file is stored raw in the request
            upload = request
            is_raw = True
            try:
                filename = request.GET[ 'qqfile' ]
            except KeyError:
                return HttpResponseBadRequest( "AJAX request not valid" )
        # not an ajax upload, so it was the "basic" iframe version with submission via form
        else:
            is_raw = False
            if len( request.FILES ) == 1:
              # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
              # ID based on a random number, so it cannot be guessed here in the code.
              # Rather than editing Ajax Upload to pass the ID in the querystring, note that
              # each upload is a separate request so FILES should only have one entry.
              # Thus, we can just grab the first (and only) value in the dict.
                upload = request.FILES.values( )[ 0 ]
            else:
                raise Http404( "Bad Upload" )
            filename = upload.name

    filename=smart_unicode(filename, encoding='utf-8', strings_only=False, errors='strict')
    filename=request.user.username + '.png'
    # save the file
    success,url = user_picture_upload(request, upload, filename, is_raw )

    # let Ajax Upload know whether we saved it or not
    ret_json = { 'success': success, 'url': url }
    return HttpResponse( json.dumps( ret_json ) )
  
  
def user_picture_upload(request, uploaded, filename, raw_data ):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    try:
        filename = os.path.normpath(os.path.join(settings.MEDIA_ROOT+'/profile/', filename))
        with BufferedWriter( FileIO( filename, "w" ) ) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                (dirName, fileName) = os.path.split(filename)
                print dirName
                print fileName           
                user = get_object_or_404(User,username=request.user.username)
                user_profile = UserProfile.objects.get(user=user)
                user_profile.picture.save(fileName,ContentFile(uploaded.read()))
                
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                (dirName, fileName) = os.path.split(filename)
                print fileName
                # TODO: figure out when this gets called, make it work to save into a Photo like above
                for c in uploaded.chunks( ):
                    dest.write( c )
                user = get_object_or_404(User,username=request.user.username)
                user_profile = UserProfile.objects.get(user=user)
                user_profile.picture.save(fileName,File(open(filename)))
        return True, user_profile.picture.url
    except IOError:
        # could not open the file most likely
        return False, -1
    return True, -1