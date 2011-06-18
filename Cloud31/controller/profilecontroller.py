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
 
@login_required(login_url='/signin/')
def user(request, username):
    t = loader.get_template('profile.html')
    context = RequestContext(request)
    
    user = get_object_or_404(User,username=username)
    user_profile = get_object_or_404(UserProfile,user=user)
    target_user = get_object_or_404(UserProfile, user=user)
    context['page_profile'] = "selected"
    context['target_user']=target_user
    context['profile_user']=username
    
    context['side_list']=['user_profile']
    context['current_user']=user
    context['user_profile']=user_profile
    if request.user.username == username:
        context['profile_type']='me'
    else:
        context['profile_type']='user'
    context['load_type']='user#'+username
    return HttpResponse(t.render(context))
    

def picture(request,username):
    try:
        user = get_object_or_404(User,username=username)
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.picture.name:
            return HttpResponseRedirect('/media/'+user_profile.picture.name)
    except Exception as e:
        print str(e)
            
    return HttpResponseRedirect('/media/default.png')

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
    success = user_picture_upload(request, upload, filename, is_raw )

    # let Ajax Upload know whether we saved it or not
    ret_json = { 'success': success }
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
    except IOError:
        # could not open the file most likely
        return False, -1
    return True
