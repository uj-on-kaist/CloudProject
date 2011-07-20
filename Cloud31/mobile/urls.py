from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'mobile.logincontroller.signin'),
    url(r'^logout/$', 'mobile.logincontroller.signout'),
    url(r'^login/check$', 'mobile.logincontroller.login_test'),
    
    url(r'feed/update/','mobile.feedcontroller.update'),
)