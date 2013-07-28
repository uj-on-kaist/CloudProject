from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

import django_cron
django_cron.autodiscover()


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
    url(r'^feed/detail/(?P<feed_id>\w+)$', 'controller.feedcontroller.feed_detail'),
    
    
    url(r'^api/feed/update/$','controller.feedcontroller.update_feed'),
    url(r'^api/feed/delete/(?P<feed_id>\w+)$','controller.feedcontroller.delete_feed'),
    url(r'^api/feed/favor/(?P<feed_id>\w+)$','controller.feedcontroller.favorite_action'),
    url(r'^api/feed/unfavor/(?P<feed_id>\w+)$','controller.feedcontroller.unfavorite_action'),

    url(r'^api/feed/update/comment/$','controller.feedcontroller.update_comment'),
    url(r'^api/feed/user/(?P<user_name>\w+)/$','controller.feedcontroller.load_feed'),
    url(r'^api/feed/user_at/(?P<user_name>\w+)$','controller.feedcontroller.get_user_at_feed'),
    url(r'^api/feed/favorite/(?P<user_name>\w+)$','controller.feedcontroller.load_favorite'),
    url(r'^api/feed/company$','controller.feedcontroller.load_comany_feed'),
    url(r'^api/feed/notice$','controller.feedcontroller.load_notice'),
    
    url(r'^api/feed/comment/delete/(?P<comment_id>\w+)$','controller.feedcontroller.delete_comment'),
    
    url(r'^api/timeline/me/$','controller.feedcontroller.load_my_timeline'),
    
    
    url(r'^topic/$','controller.topiccontroller.topic'),
    url(r'^topic/(?P<topic_id>\w+)/$','controller.topiccontroller.topic_detail'),
    url(r'^api/topic/favor/(?P<topic_id>\w+)$','controller.topiccontroller.topic_favorite'),
    url(r'^api/topic/unfavor/(?P<topic_id>\w+)$','controller.topiccontroller.topic_unfavorite'),
    
    url(r'^api/feed/topic/(?P<topic_id>\w+)/$','controller.topiccontroller.load_topic_timeline'),
    url(r'^api/feed/update/desc$','controller.topiccontroller.update_description'),
    
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    
    url(r'^signin/$','controller.usercontroller.signin'),
    url(r'^signout/$','controller.usercontroller.signout'),
    url(r'^signup/$','controller.usercontroller.signup'),
    url(r'^confirm/$','controller.usercontroller.confirm'),
    
    url(r'^user/(?P<username>\w+)/$','controller.profilecontroller.user'),
    url(r'^favorite/$','controller.profilecontroller.favorite'),
    url(r'^picture/(?P<username>\w+)/$','controller.profilecontroller.picture'),
    url(r'^picture/(?P<size>\w+)/(?P<username>\w+)/$','controller.profilecontroller.picture_size'),

    url(r'^file/$', 'controller.filecontroller.main'),
    url(r'^file/download/(?P<file_id>\w+)$', 'controller.filecontroller.download_file'),
    url(r'^file/download2/(?P<file_info>.+)$', 'controller.filecontroller.download_file_2'),
    url(r'^file/ajax_upload$', 'controller.filecontroller.ajax_upload'),
    
    url(r'^members/$', 'controller.membercontroller.main'),
    
    url(r'^location/$', 'controller.locationcontroller.main'),
    url(r'^api/location/random$', 'controller.locationcontroller.get_random_feeds'),
    url(r'^api/location/get$', 'controller.locationcontroller.get_location_feeds'),
    
    
    url(r'^message/$', 'controller.messagecontroller.main'),
    url(r'^message/new$', 'controller.messagecontroller.new'),
    url(r'^message/detail/(?P<message_id>\w+)$', 'controller.messagecontroller.message_detail'),
    url(r'^api/message/update/$','controller.messagecontroller.send_message'),
    url(r'^api/message/reply/update/$','controller.messagecontroller.reply_message'),
    url(r'^api/message/reply/delete/(?P<reply_id>\w+)$','controller.messagecontroller.delete_reply'),
    url(r'^api/message/delete/(?P<message_id>\w+)$','controller.messagecontroller.delete_message'),
    url(r'^api/message/get/(?P<load_type>\w+)/$','controller.messagecontroller.load_message'),
    
    
    url(r'^poll/$', 'controller.pollcontroller.main'),
    url(r'^poll/new$', 'controller.pollcontroller.new'),
    url(r'^poll/detail/(?P<poll_id>\w+)$', 'controller.pollcontroller.detail_poll'),
    url(r'^api/poll/register/$','controller.pollcontroller.register_poll'),
    url(r'^api/poll/delete/(?P<poll_id>\w+)$','controller.pollcontroller.delete_poll'),
    url(r'^api/poll/update/comment/$','controller.pollcontroller.update_poll_comment'),
    url(r'^api/poll/comment/delete/(?P<comment_id>\w+)$','controller.pollcontroller.delete_poll_comment'),
    url(r'^api/poll/delete/(?P<poll_id>\w+)$','controller.pollcontroller.delete_poll'),
    url(r'^api/poll/option/(?P<option_info>.+)$','controller.pollcontroller.check_option'),
    
    url(r'^event/$', 'controller.eventcontroller.main'),
    url(r'^event/new$', 'controller.eventcontroller.new'),
    url(r'^event/detail/(?P<event_id>\w+)$', 'controller.eventcontroller.detail_event'),
    url(r'^api/event/detail/(?P<event_id>\w+)$', 'controller.eventcontroller.event_detail'),
    url(r'^api/event/attend/(?P<event_id>\w+)$', 'controller.eventcontroller.attend_event'),
    url(r'^api/event/register/$','controller.eventcontroller.register_event'),
    url(r'^api/event/comment/delete/(?P<comment_id>\w+)$','controller.eventcontroller.delete_event_comment'),
    url(r'^api/event/delete/(?P<event_id>\w+)$','controller.eventcontroller.delete_event'),
    url(r'^api/event/get/(?P<load_type>\w+)$','controller.eventcontroller.load_event'),
    
    
    url(r'^api/event/get_info$','controller.eventcontroller.get_info'),
    url(r'^api/event/get_info_date$','controller.eventcontroller.get_info_date'),
    
    url(r'^api/event/update/comment/$','controller.eventcontroller.update_event_comment'),
    
    
    url(r'^notifications/$', 'controller.notificationcontroller.main'),
    url(r'^notifications/read$', 'controller.notificationcontroller.read'),
    url(r'^notifications/unread$', 'controller.notificationcontroller.unread'),
    
    url(r'^api/noti/get/$', 'controller.notificationcontroller.get_notifications'),
    url(r'^api/noti/get/(?P<typed>\w+)$', 'controller.notificationcontroller.get_typed_notifications'),
    url(r'^api/noti/read/(?P<noti_id>\w+)$', 'controller.notificationcontroller.read_notification'),
    
    
    url(r'^setting/$', 'controller.settingcontroller.setting'),
    url(r'setting/update/(?P<update_type>\w+)$', 'controller.settingcontroller.update'),
    url(r'^setting/picture/set$', 'controller.settingcontroller.ajax_upload'),
    
    
    url(r'^search/(?P<keyword>.*)$', 'controller.searchcontroller.main'),
    url(r'^api/search/user$', 'controller.searchcontroller.ajax_user'),
    url(r'^api/search/topic$', 'controller.searchcontroller.ajax_topic'),
    
    
    
    url(r'^api/sidebar/dialog/add$', 'sidebar.sidebarcontroller.add_dialog'),
    url(r'^api/sidebar/dialog/delete$', 'sidebar.sidebarcontroller.delete_dialog'),
    url(r'^api/sidebar/dialog/get$', 'sidebar.sidebarcontroller.load_dialog'),
    url(r'^api/sidebar/invite$', 'sidebar.sidebarcontroller.send_invite'),
    url(r'^api/sidebar/poll/get$', 'sidebar.sidebarcontroller.load_poll'),

    
    
    url(r'^chart/test$','controller.statisticcontroller.test'),
    url(r'^chart/recent_user$','controller.statisticcontroller.recent_user_graph'),
    url(r'^chart/recent_message$','controller.statisticcontroller.recent_message_graph'),
    url(r'^chart/recent_pop_topics$','controller.statisticcontroller.recent_pop_topics'),
    url(r'^chart/recent_active_users$','controller.statisticcontroller.recent_active_users'),
    url(r'^chart/recent_user_stats/(?P<user_id>\w+)$','controller.statisticcontroller.recent_user_stats'),
    url(r'^chart/recent_topic_stats/(?P<topic_id>\w+)$','controller.statisticcontroller.recent_topic_stats'),
        
        
    url(r'^tab/$','controller.tabcontroller.tab'),
    url(r'^tab/(?P<tab_id>\w+)$','controller.tabcontroller.tab_detail'),
    
    url(r'^admin/overview','controller.admincontroller.overview'),
    url(r'^admin/stats/topic/$','controller.admincontroller.stats_topic'),
    url(r'^admin/stats/thread/$','controller.admincontroller.stats_thread'),
    url(r'^admin/stats/favorite/$','controller.admincontroller.stats_favorite'),
    url(r'^admin/stats/member','controller.admincontroller.stats_member'),
    
    url(r'^admin/export/$','controller.admincontroller.export'),
    url(r'^admin/export/process/test$','controller.exportcontroller.process_test'),
    url(r'^admin/export/process/$','controller.exportcontroller.process'),
    
    url(r'^admin/authority/$','controller.admincontroller.authority'),
    url(r'^admin/authority/update/$','controller.admincontroller.authority_update'),
    
    url(r'^admin/invite/$','controller.admincontroller.invite'),
    url(r'^admin/invite/send/$','controller.admincontroller.send_invites'),
    
    url(r'^admin/tab/$','controller.tabcontroller.tab_admin'),
    url(r'^admin/tab/manage/(?P<tab_id>\w+)$','controller.tabcontroller.tab_manage'),
    url(r'^admin/tab/delete$','controller.tabcontroller.tab_delete'),

    url(r'^admin/notice/$','controller.admincontroller.notice'),
    url(r'^api/notice/update/$','controller.admincontroller.update_notice'),
    url(r'^api/notice/delete/(?P<notice_id>\w+)$','controller.admincontroller.delete_notice'),
    
    url(r'^admin/dashboard/$','controller.admincontroller.dashboard'),
    
    url(r'^mobile/',include('mobile.urls')),
)
