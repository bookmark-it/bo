from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets
from .models import Friend, FriendshipRequest
from bookmarks.serializers import UserSerializer
import json


User = get_user_model()

class FriendUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=100)


class FriendshipRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRequest
        fields = ('id', 'from_user', 'to_user', 'message', 'created', 'rejected', 'viewed')

    def create(self, validated_data):
        """ create a friendship request """

        request = Friend.objects.add_friend(from_user=validated_data['from_user'],
                                            to_user=validated_data['to_user'],
                                            message=validated_data['message'])

        return request




class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friend
        fields = ('from_user', 'to_user')
