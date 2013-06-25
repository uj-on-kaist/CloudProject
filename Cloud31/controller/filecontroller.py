from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader

from django.views.decorators.csrf import csrf_exempt

from io import BufferedWriter,FileIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files import File
from django.contrib.auth.decorators import login_required
from controller import models
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

from django.utils.encoding import smart_unicode, smart_str

def upload_page( request ):
    t = loader.get_template('upload_page.html')
    context = RequestContext(request)
    return HttpResponse(t.render(context))
    

import os, json, mimetypes
import my_utils
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.core.servers.basehttp import FileWrapper

from django.conf import settings

@login_required(login_url='/signin/')
def download_file(request, file_id, file_name):
    print file_name
    target_file = get_object_or_404(models.File,id=file_id)
    agent = request.META['HTTP_USER_AGENT']
    print agent
    try:
        path = target_file.file_contents.path
        content_type = mimetypes.guess_type( path )[0]
        my_data = File(open(path))
        response = HttpResponse(my_data,content_type=content_type)
        response['Content-Length'] = target_file.file_contents.size
        file_name = smart_unicode(target_file.file_name, encoding='utf-8', strings_only=False, errors='strict')
        response['Content-Disposition'] = 'attachment;'
        """
        response['Content-Disposition'] = 'attachment; filename=\"' + smart_str(target_file.file_name) +'\"'
        if 'MSIE' in agent:
            print "1Agent "+agent
            (fileBaseName, fileExtension)=os.path.splitext(smart_str(file_name))
            asdf = unicode("attachment; filename=\"download"+fileExtension+"\"")
            import unicodedata
            asdf = unicodedata.normalize('NFKD', asdf).encode('ascii','ignore')
            response['Content-Disposition'] = asdf
        """
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Cache-Control'] = 'no-cache'
    except Exception as e:
        print str(e)
    return response


def download_file_2(request, file_info):
    """
    THIS IS FILE_DOWNLOAD HANDLED VERSION FOR IE.
    """
    
    file_info = file_info.split('/')
    file_id = file_info[0]
    file_name = file_info[1]
    target_file = get_object_or_404(models.File,id=file_id)
    agent = request.META['HTTP_USER_AGENT']
    try:
        path = target_file.file_contents.path
        content_type = mimetypes.guess_type( path )[0]
        if content_type is None:
            content_type = 'application/octet-stream'
        my_data = File(open(path))
        response = HttpResponse(my_data,content_type=content_type)
        response['Content-Length'] = target_file.file_contents.size
        response['Content-Disposition'] = 'attachment;'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Cache-Control'] = 'no-cache'
    except Exception as e:
        print str(e)
    return response
    
    
    
@login_required(login_url='/signin/')
def main(request):
    t = loader.get_template('file.html')
    context = RequestContext(request)
    my_utils.load_basic_info(request, context)
    
    context['side_list']=['search_file']
    context['page_files'] = "selected"
    
    my_utils.prepare_search_topic(context)
    
    context['files']=list()
    try:
        keyword = request.GET.get('q', '')
        query_type = Q()
        if keyword is not '':
            print keyword
            query_type = Q(file_name__icontains=keyword)
        
        search_index = request.GET.get('index', '')

        if search_index is not '':
            if search_index in map(chr, range(65, 91)):
                query_type = Q(file_name__istartswith=search_index)
            elif search_index == 'number':
                query_type = Q(file_name__gt="0",file_name__lt="9")
            else:
                this_index,next_index=my_utils.next_search_index(search_index)
                query_type = Q(file_name__gt=this_index, file_name__lt=next_index)
        
        files = models.File.objects.filter(query_type, is_attached=True).order_by('file_name')
        files = my_utils.process_files(files)
        
        paginator = Paginator(files, 15)
        
        page = request.GET.get('page', 1)
        try:
            context['files'] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context['files'] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context['files'] = paginator.page(paginator.num_pages)
        
        context['index_info'] = my_utils.get_index_list(context['files'].number, paginator.num_pages)
        
    except Exception as e:
        print str(e)
        
    
    
    return HttpResponse(t.render(context))

import uuid
def save_upload(request, uploaded, filename, raw_data ):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    try:
        user = get_object_or_404(User,username=request.user.username)
        input_file_name = filename
        (fileBaseName, fileExtension)=os.path.splitext(filename)
        real_file_name = user.username + "_" + str(uuid.uuid1()) + fileExtension
        filename = os.path.normpath(os.path.join(settings.MEDIA_ROOT+'/files/', real_file_name))
        
        with BufferedWriter( FileIO( filename, "w" ) ) as dest:
            # if the "advanced" upload, read directly from the HTTP request
            # with the Django 1.3 functionality
            if raw_data:
                (dirName, fileName) = os.path.split(filename)
                (fileBaseName, fileExtension)=os.path.splitext(fileName)
                fileExtension=fileExtension[1:]
                print fileName+"['"+fileBaseName+ "','"+fileExtension+"']"
                
                
                new_file = models.File(file_type=fileExtension,file_name=input_file_name, uploader=user)
                new_file.file_contents.save(fileName,ContentFile(uploaded.read()))
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                (dirName, fileName) = os.path.split(filename)
                (fileBaseName, fileExtension)=os.path.splitext(fileName)
                fileExtension=fileExtension[1:]
                print "2 " + fileName+"['"+fileBaseName+ "','"+fileExtension+"']"
                
                # TODO: figure out when this gets called, make it work to save into a Photo like above
                for c in uploaded.chunks():
                    dest.write( c )
                
                dest.close()
                new_file = models.File(file_type=fileExtension,file_name=input_file_name, uploader=user)
                fileName2 = user.username + "_" + str(uuid.uuid1()) +'.'+ fileExtension
                new_file.file_contents.save(fileName2,File(open(filename)))
                new_file.save()

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
  
    