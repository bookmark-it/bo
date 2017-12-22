from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Hook(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hook')
    url = models.URLField(max_length=250)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u"%s" % self.url
