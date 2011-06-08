from django.conf.urls.defaults import patterns, include, url
from django.conf import settings


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Cloud31.views.home', name='home'),
    # url(r'^Cloud31/', include('Cloud31.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$','controller.maincontroller.main'),
    
    url(r'^feed/$','controller.feedcontroller.feed'),
    
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    
    url(r'^signin/$','controller.usercontroller.signin'),
    url(r'^signout/$','controller.usercontroller.signout'),
    url(r'^signup/$','controller.usercontroller.signup'),
    url(r'^confirm/$','controller.usercontroller.confirm'),
    
    url(r'^user/(?P<username>\w+)/$','controller.profilecontroller.user'),
    
    url(r'file/ajax_upload$', 'controller.filecontroller.ajax_upload'),
    url(r'file/$', 'controller.filecontroller.upload_page' ),
)
