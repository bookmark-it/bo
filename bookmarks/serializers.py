from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Bookmark, Category, Keyword, Folder, Website, BookmarksUser, Notification
from friends.models import Friend

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')

class FriendSerializer(serializers.ModelSerializer):
    to_user = UserSerializer(many=False, read_only=True)
    from_user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Friend
        fields = ('id','to_user', 'from_user', 'created')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id','user', 'notification_type', 'name', 'short_text')

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('id', 'name', 'website_type', 'url')

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('id', 'name')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'icon_code')


class BookmarkSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    keywords = KeywordSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    class Meta:
        model = Bookmark
        fields = ('id', 'url', 'user', 'title', 'description', 'source', 'image_url', 'favicon_url', 'categories', 'keywords', 'favorite', 'toread', 'added_datetime', 'edit_datetime')

    def create(self, validated_data):
        user = None
        category_list = []
        keywords = []

        request = self.context['request']
        if request and hasattr(request, "user") and not hasattr(request.user, 'hook'):
            user = request.user
            validated_data['user'] = user

        if 'categories' in validated_data:
            category_list = validated_data.pop('categories')

        if 'keywords' in validated_data:
            keywords = validated_data.pop('keywords')

        bookmark = Bookmark.objects.create(**validated_data)

        for cat in category_list:
            category, _ = Category.objects.get_or_create(**cat)
            bookmark.categories.add(category)

        for key in keywords:
            keyword, _ = Keyword.objects.get_or_create(**key)
            bookmark.keywords.add(keyword)

        return bookmark

    def update(self, instance, validated_data):
        category_list = []
        keyword_list = []

        categories_data = validated_data.pop('categories', [])
        keywords_data = validated_data.pop('keywords', [])

        for cat in categories_data:
            category, created = Category.objects.get_or_create(**cat)
            category_list.append(category)
        instance.categories = category_list

        for key in keywords_data:
            keyword, _ = Keyword.objects.get_or_create(**key)
            keyword_list.append(keyword)
        instance.keywords = keyword_list

        for key in validated_data:
            setattr(instance, str(key), validated_data.get(key))
        instance.save()
        return instance

class FolderParentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    class Meta:
        model = Folder
        fields = ('id', 'user', 'name', 'public')
        read_only_fields = ('user', 'id', 'name', 'public')


class FolderSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    bookmarks = BookmarkSerializer(many=True, read_only=True)
    authorised_users = UserSerializer(many=True, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    #folder_set = FolderParentSerializer(many=False, read_only=True)
    parent = FolderParentSerializer(many=False, read_only=True)
    children_directories = FolderParentSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'user', 'name', 'authorised_users', 'parent', 'added_datetime', 'bookmarks', 'children_directories', 'public', 'sharecount')
        read_only_fields = ('user', 'id', 'sharecount')


class BookmarksSerializer(serializers.Serializer):
    bookmarks = BookmarkSerializer(many=True)

class ShareSerializer(serializers.Serializer):
    to = serializers.ListField(child=serializers.EmailField())
    url = serializers.URLField()
    title = serializers.CharField()

    class Meta:
        #model = Folder
        fields = ('id', 'to', 'url', 'title', 'user')
