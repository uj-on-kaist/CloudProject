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
    
