from django.contrib import admin
from .models import BookmarksUser, Category, Bookmark, Keyword, Folder, BlacklistedWebsites, WebsiteType, Website, Notification
# Register your models here.

admin.site.register(Bookmark)
admin.site.register(Category)
admin.site.register(Folder)
admin.site.register(Keyword)
admin.site.register(Website)
admin.site.register(WebsiteType)
admin.site.register(BlacklistedWebsites)
admin.site.register(BookmarksUser)
admin.site.register(Notification)
