from django.conf.urls import url
from friends.views import FriendViewSet, FriendshipRequestViewSet

friends_list = FriendViewSet.as_view({
    'get': 'list'
})

friendship_list = FriendshipRequestViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

friendship_details = FriendshipRequestViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy',
    'put': 'update'
})

friendship_outgoing = FriendshipRequestViewSet.as_view({
    'get': 'outgoing_list'
})

friendship_incoming = FriendshipRequestViewSet.as_view({
    'get': 'incoming_list'
})

friendship_validation = FriendshipRequestViewSet.as_view({
    'get': 'accept'
})

friendship_rejection = FriendshipRequestViewSet.as_view({
    'get': 'reject'
})



urlpatterns = [
    url(r'^friends/$', friends_list, name='friends-list'),
    url(r'^requests/$', friendship_list, name='Friendship-incoming'),
    url(r'^requests/incoming/$', friendship_incoming, name='Friendship-incoming'),
    url(r'^requests/outgoing/$', friendship_outgoing, name='Friendship-outgoing'),
    url(r'^friendships/(?P<pk>[0-9]+)/$', friendship_details, name='Friendship-details'),
    url(r'^requests/accept/(?P<pk>[0-9]+)/$', friendship_validation, name='Friendship-acceptation'),
    url(r'^requests/reject/(?P<pk>[0-9]+)/$', friendship_rejection, name='Friendship-rejection'),
]
