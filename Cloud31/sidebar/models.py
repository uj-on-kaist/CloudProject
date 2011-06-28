from django.db import models
from django.contrib.auth.models import User

class Dialog(models.Model):
    author = models.ForeignKey(User)
    contents = models.TextField(null=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)