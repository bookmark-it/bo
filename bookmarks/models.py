from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import datetime

class WebsiteType(models.Model):
    wtype = models.CharField(max_length=20, blank=True)
    def __unicode__(self):
        return u"%s" % self.wtype

class BlacklistedWebsites(models.Model):
    url = models.URLField(max_length=250)
    def __unicode__(self):
        return u"%s" % self.url

class Website(models.Model):
    name = models.CharField(max_length=20, blank=True)
    website_type = models.ManyToManyField(WebsiteType, blank=True)
    url = models.URLField(max_length=250)
    def __unicode__(self):
        return u"%s" % self.url

class Keyword(models.Model):
    name = models.CharField(max_length=20, unique=True)
    def __unicode__(self):
        return u"%s" % self.name



class BookmarksUser(models.Model):
    DEFAULT_BOOKMARK_VIEWTYPE = (
        ('BOX', 'Boxes'),
        ('BLI', 'Big List'),
        ('SLI', 'Small List'),
    )
    OPEN_BK_OPTIONS = (
        ('TAB', 'New tab'),
        ('WIN', 'New Window'),
    )
    USER_LEVELS = (
        ('FREE', 'Free'),
        ('PAID', 'Paid'),
        ('CORP', 'Corporate'),
        ('ORGS', 'Organisation'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_bk_view = models.CharField(max_length=3, choices=DEFAULT_BOOKMARK_VIEWTYPE, default="BLI")
    open_bk_option = models.CharField(max_length=3, choices=OPEN_BK_OPTIONS, default="TAB")
    user_level = models.CharField(max_length=4, choices=USER_LEVELS, default="CORP")
    public = models.BooleanField(default=False)
    #area of expertise
    #linkedIn work position verification, fetch skills, fetch current position
    #social_media_accounts
    #quick_lists
    last_data_clean = models.DateTimeField(blank=True, null=True)
    #clean frequency --> send user_level preferences to another table
    def __unicode__(self):
        return u"%s" % self.user.username




class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('FRIEND', 'Friend Request'),
        ('SHARE', 'Shared with you'),
        ('MESSAGE', 'Message'),
        ('FOLDER', 'Folder activity'),
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    url = models.URLField(max_length=250)
    notification_type = models.CharField(max_length=7, choices=NOTIFICATION_TYPES, null=True, blank=True)
    name = models.CharField(max_length=20)
    short_text = models.CharField(max_length=75)
    added_datetime = models.DateTimeField(auto_now_add=True, null=True)
    seen = models.BooleanField(default=False)
    def __unicode__(self):
        return u"%s" % self.name


class Category(models.Model):
    #user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=20)
    icon_code = models.CharField(max_length=20)
    added_datetime = models.DateTimeField(auto_now_add=True, null=True)
    edit_datetime = models.DateTimeField(auto_now=True, null=True)
    def __unicode__(self):
        return u"%s" % self.name


class Bookmark(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='user')

    url = models.URLField(max_length=250)
    source = models.URLField(max_length=250, blank=True)
    title = models.CharField(max_length=250, blank=True)
    description = models.CharField(max_length=250, blank=True)

    favorite = models.BooleanField(default=False)
    tosort = models.BooleanField(default=False)
    toread = models.BooleanField(default=False)

    image_url = models.URLField(max_length=250, blank=True)
    favicon_url = models.URLField(max_length=250, blank=True)

    categories = models.ManyToManyField(Category, blank=True)
    keywords = models.ManyToManyField(Keyword, blank=True)


    friends = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    verified = models.BooleanField(default=False) #by marvin or by peers ?

    # number of open
    # number of shares or bool has been shared
    added_datetime = models.DateTimeField(auto_now_add=True, null=True)
    edit_datetime = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return u"%s" % self.title


    class Meta:
        unique_together = ('user', 'url')
        ordering = ('edit_datetime', 'added_datetime')


class Folder(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)
    authorised_users = models.ManyToManyField(User, blank=True, related_name="authorised_users")
    parent = models.ForeignKey('Folder', blank=True, null=True, related_name="children_directories", on_delete=models.CASCADE)
    added_datetime = models.DateTimeField(auto_now_add=True, null=True)
    edit_datetime = models.DateTimeField(auto_now=True, null=True)
    bookmarks = models.ManyToManyField(Bookmark, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    @property
    def sharecount(self):
        return len(self.authorised_users.all())
