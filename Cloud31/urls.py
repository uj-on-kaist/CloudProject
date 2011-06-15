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
    
    
    url(r'^api/feed/update/$','controller.feedcontroller.update_feed'),
    url(r'^api/feed/delete/(?P<feed_id>\w+)$','controller.feedcontroller.delete_feed'),
    url(r'^api/feed/favor/(?P<feed_id>\w+)$','controller.feedcontroller.favorite_action'),
    url(r'^api/feed/unfavor/(?P<feed_id>\w+)$','controller.feedcontroller.unfavorite_action'),

    url(r'^api/feed/update/comment/$','controller.feedcontroller.update_comment'),
    url(r'^api/feed/user/(?P<user_name>\w+)/$','controller.feedcontroller.load_feed'),
    url(r'^api/feed/favorite/(?P<user_name>\w+)$','controller.feedcontroller.load_favorite'),
    url(r'^api/feed/company$','controller.feedcontroller.load_comany_feed'),
    url(r'^api/feed/notice$','controller.feedcontroller.load_notice'),
    
    url(r'^api/comment/delete/(?P<comment_id>\w+)$','controller.feedcontroller.delete_comment'),
    
    url(r'^api/timeline/me/$','controller.feedcontroller.load_my_timeline'),

    
    
    
    
    url(r'^topic/$','controller.topiccontroller.topic'),
    url(r'^topic/(?P<topic_name>\w+)/$','controller.topiccontroller.topic_detail'),
    url(r'^api/feed/topic/(?P<topic_name>\w+)/$','controller.topiccontroller.load_topic_timeline'),

    
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    
    url(r'^signin/$','controller.usercontroller.signin'),
    url(r'^signout/$','controller.usercontroller.signout'),
    url(r'^signup/$','controller.usercontroller.signup'),
    url(r'^confirm/$','controller.usercontroller.confirm'),
    
    url(r'^user/(?P<username>\w+)/$','controller.profilecontroller.user'),

    url(r'^picture/set$', 'controller.profilecontroller.ajax_upload'),
    url(r'^picture/(?P<username>\w+)/$','controller.profilecontroller.picture'),

    url(r'file/ajax_upload$', 'controller.filecontroller.ajax_upload'),
    
    url(r'setting/$', 'controller.settingcontroller.setting'),
    
    
    url(r'message/$', 'controller.messagecontroller.main'),
    url(r'message/(?P<message_id>\w+)$', 'controller.messagecontroller.message_detail'),
    url(r'^api/message/update/$','controller.messagecontroller.send_message'),
    url(r'^api/message/delete/(?P<message_id>\w+)$','controller.messagecontroller.delete_message'),
    url(r'^api/message/get/(?P<load_type>\w+)/$','controller.messagecontroller.load_message'),
    
    url(r'^api/search/user$', 'controller.searchcontroller.ajax_user'),
    
    
    url(r'^event/$', 'controller.eventcontroller.main'),

)
