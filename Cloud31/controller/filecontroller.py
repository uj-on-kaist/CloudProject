from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from django.views.decorators.csrf import csrf_exempt

from io import BufferedWriter,FileIO

from django.conf import settings
from django.core.files.base import ContentFile

from controller.models import *
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

from django.utils.encoding import smart_unicode

def upload_page( request ):
    t = loader.get_template('upload_page.html')
    context = RequestContext(request)
    return HttpResponse(t.render(context))
    

import os, json

def save_upload(request, uploaded, filename, raw_data ):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    try:
        filename = os.path.normpath(os.path.join(settings.MEDIA_ROOT+'/files/', filename))
        with BufferedWriter( FileIO( filename, "w" ) ) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                (dirName, fileName) = os.path.split(filename)
                (fileBaseName, fileExtension)=os.path.splitext(fileName)
                fileExtension=fileExtension[1:]
                print fileName+"['"+fileBaseName+ "','"+fileExtension+"']"
                
                user = get_object_or_404(User,username=request.user.username)
                new_file = File(file_type=fileExtension,file_name=fileName, uploader=user)
                new_file.file_contents.save(fileName,ContentFile(uploaded.read()))
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                # TODO: figure out when this gets called, make it work to save into a Photo like above
                for c in uploaded.chunks( ):
                    dest.write( c )
    except IOError:
        # could not open the file most likely
        return False, -1
    return True, new_file.id


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
  # save the file
  success, file_id = save_upload(request, upload, filename, is_raw )

  # let Ajax Upload know whether we saved it or not
  ret_json = { 'success': success, 'id': file_id}
  return HttpResponse( json.dumps( ret_json ) )