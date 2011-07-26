from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	activation_key = models.CharField(max_length=40)
	key_expires = models.DateTimeField()
	dept = models.CharField(max_length=50)
	position = models.CharField(max_length=50)
	is_deactivated = models.BooleanField(default=False)
	receive_email = models.BooleanField(default=True)
	receive_apns = models.BooleanField(default=True)
	device_id = models.CharField(max_length=50)
	picture = models.ImageField(upload_to="profile", default='/media/default.png')
	
##  
## Message Related
##
class Message(models.Model):
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    lat = models.CharField(max_length=30,default='')
    lng = models.CharField(max_length=30,default='')
    write_from = models.CharField(max_length=30,default='')
    # Comma Seperated
    attach_files = models.TextField(default='')
    related_users = models.TextField(default='')
    related_topics = models.TextField(default='')


class Comment(models.Model):
    message = models.ForeignKey(Message)
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class File(models.Model):
    file_type = models.CharField(max_length=10)
    file_contents = models.FileField(upload_to='files',null=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    uploader = models.ForeignKey(User)
    file_name = models.CharField(max_length=256)
    is_attached = models.BooleanField(default=False)


class Notice(models.Model):
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    location = models.CharField(max_length=30,default='')
    write_from = models.CharField(max_length=30,default='')
    # Comma Seperated
    attach_files = models.TextField(default='')
    related_users = models.TextField(default='')
    related_topics = models.TextField(default='')

##  
## Topic Related
##
class Topic(models.Model):
    topic_name = models.CharField(max_length=50, unique=True, null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    # Comma Seperated
    related_topics = models.TextField(default='')
    topic_detail = models.TextField(default='')
    reference_count = models.IntegerField(default=0)

    
class TopicTimeline(models.Model):
    message = models.ForeignKey(Message)
    topic = models.ForeignKey(Topic)
    update_date = models.DateTimeField(auto_now=True)

##  
## User Related
##
class UserTimeline(models.Model):
    message = models.ForeignKey(Message)
    user = models.ForeignKey(User)
    update_date = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
        
class UserFavorite(models.Model):
    message = models.ForeignKey(Message)
    user = models.ForeignKey(User)
    reg_date = models.DateTimeField(auto_now_add=True)

class UserTopicFavorite(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
    reg_date = models.DateTimeField(auto_now_add=True)

class UserNotification(models.Model):
    user = models.ForeignKey(User, related_name="receiver")
    sender = models.ForeignKey(User, related_name="sender")
    notification_type = models.CharField(max_length=10)
    related_type = models.CharField(max_length=10)
    related_id = models.IntegerField()
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

##  
## Event Related
##
class Event(models.Model):
    host = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    location = models.CharField(max_length=100)
    map_info = models.CharField(max_length=30,default='')
    
    # Comma Seperated
    invited_users = models.TextField(default='')
    
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)


class EventComment(models.Model):
    event = models.ForeignKey(Event)
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

class EventParticipate(models.Model):
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    attend_status = models.CharField(max_length=10, default='')

##  
## Direct Message Related
##
class DirectMessage(models.Model):
    author = models.ForeignKey(User)
    receivers = models.TextField(null=False)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    

class DirectMessageReply(models.Model):
    direct_message = models.ForeignKey(DirectMessage)
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


##  
## Notification Queue
##
class EmailQueue(models.Model):
    target_email = models.CharField(max_length=60, default='')
    subject = models.TextField(null=False)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)


class NotificationQueue(models.Model):
    notification_type = models.CharField(max_length=20)
    target_user = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

