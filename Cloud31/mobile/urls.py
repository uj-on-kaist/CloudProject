from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'mobile.logincontroller.signin'),
    url(r'^logout/$', 'mobile.logincontroller.signout'),
    url(r'^login/check$', 'mobile.logincontroller.login_test'),

    url(r'feed/update/','mobile.feedcontroller.update'),
    url(r'feed/delete/(?P<feed_id>\w+)','mobile.feedcontroller.delete'),
    url(r'feed/comment/update/','mobile.feedcontroller.update_comment'),
    url(r'feed/get/(?P<feed_id>\w+)','mobile.feedcontroller.get_feed'),
    
    url(r'file/upload','mobile.filecontroller.file_upload'),
    url(r'picture/upload','mobile.filecontroller.picture_upload'),
    
    url(r'topic/detail/(?P<topic_id>\w+)','mobile.topiccontroller.detail'),
    url(r'^topic/popular/','mobile.topiccontroller.popular'),
    url(r'^feed/topic/(?P<topic_id>\w+)/$','mobile.topiccontroller.load_topic_timeline'),
    
    url(r'^user/detail/(?P<username>\w+)/$','mobile.usercontroller.detail'),
    
    
    url(r'^search/feed/','mobile.searchcontroller.feed'),
    url(r'^search/topic/','mobile.searchcontroller.topic'),
    url(r'^search/member/','mobile.searchcontroller.member'),
    url(r'^search/file/','mobile.searchcontroller.search_file'),
    
    url(r'^noti/get/','mobile.notificationcontroller.get_notifications'),
    url(r'^noti/read/(?P<noti_id>\w+)','mobile.notificationcontroller.read_notification'),
    
    
    url(r'message/get/(?P<message_id>\w+)','mobile.messagecontroller.get_message'),
    url(r'message/update/','mobile.messagecontroller.send_message'),
    url(r'message/delete/(?P<message_id>\w+)','mobile.messagecontroller.delete_message'),
    url(r'message/reply/update/','mobile.messagecontroller.reply_message'),
)