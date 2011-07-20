from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'mobile.logincontroller.signin'),
    url(r'^logout/$', 'mobile.logincontroller.signout'),
    url(r'^login/check$', 'mobile.logincontroller.login_test'),

    url(r'feed/update/','mobile.feedcontroller.update'),
    url(r'feed/comment/update/','mobile.feedcontroller.update_comment'),
    url(r'feed/get/(?P<feed_id>\w+)','mobile.feedcontroller.get_feed'),
    
    url(r'file/upload','mobile.filecontroller.file_upload'),    
)