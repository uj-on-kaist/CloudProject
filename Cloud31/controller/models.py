from django.db import models
from django.contrib.auth.models import User

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
	picture = models.ImageField(upload_to="profile", blank=True)
    
##  
## Message Related
##
class Message(models.Model):
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    location = models.CharField(max_length=30,default='')
    
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

##  
## Topic Related
##
class Topic(models.Model):
    topic_name = models.CharField(max_length=50, unique=True, null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    # Comma Seperated
    related_topics = models.TextField(default='')
    
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
        
class UserFavorite(models.Model):
    message = models.ForeignKey(Message)
    user = models.ForeignKey(User)

class UserTopicFavorite(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)

class UserNotification(models.Model):
    user = models.ForeignKey(User)
    notification_type = models.CharField(max_length=10)
    related_type = models.CharField(max_length=10)
    related_id = models.IntegerField()
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    

##  
## Direct Message Related
##
class DirectMessage(models.Model):
    author = models.ForeignKey(User)
    receivers = models.TextField(default='')
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
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
class NotificationQueue(models.Model):
    notification_type = models.CharField(max_length=10)
    target_user = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

