from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^api/', include('bookmarks.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^friends/', include('friends.urls'))
]
