from django.conf.urls import include, url
from . import views
from rest_framework import routers


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'bookmarks', views.BookmarkViewSet, 'bookmarks')
router.register(r'categories', views.CategoryViewSet, 'categories')
router.register(r'keywords', views.KeywordViewSet, "keywords")
router.register(r'folders', views.FolderViewSet, 'folders')
router.register(r'notifications', views.NotificationViewSet, 'notifications')
router.register(r'websites', views.WebsiteViewSet, 'websites')
router.register(r'friends', views.FriendsViewSet, 'bk-friends')

router.register(r'share/$', views.Share, 'share')

router.register(r'public-bookmarks', views.PublicBookmarkViewSet, 'public-bookmarks')


urlpatterns = [
    url(r'^', include(router.urls), name='api-root'),
    url(r'^search/$', views.query.as_view({'get': 'list'})),
    url(r'^auth/me/upload', views.Upload.as_view({'get': 'list'})),
    url(r'^auth/me/$', views.MeView.as_view({'get': 'retrieve'}), name='me'),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
