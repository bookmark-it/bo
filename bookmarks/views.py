from __future__ import absolute_import, unicode_literals
from celery import shared_task 

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import status, permissions, viewsets, generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.pagination import PageNumberPagination

from django.db.models import Count

from .utils import forwardRequest
from .models import Category, Bookmark, Keyword, Folder, Website, BookmarksUser, Notification
from .serializers import BookmarkSerializer, CategorySerializer, KeywordSerializer, FolderSerializer, \
    WebsiteSerializer, UserSerializer, ShareSerializer, FriendSerializer, NotificationSerializer

from django.contrib.auth.models import User
from friends.models import Friend

import json


from communication.email import postman, library
from communication.webminer import webman
from communication.fileimport import netscape_bookmarkfile_parser as nbp

@shared_task(bind=True)
def tempCeleryFunction(self, request, bookmark, serializer) : 
    add_info = webman.retrieveUrlContent(serializer.data)
    serializer = BookmarkSerializer(bookmark, data = add_info, context={'request':request})
    if serializer.is_valid():
        serializer.save()
        print(serializer.data)
    else :
        print(serializer.errors)




class BookmarkViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookmarkSerializer
    pagination_class = PageNumberPagination


    def list(self, request):
        queryset = []
        if request.user.is_authenticated:
            queryset = Bookmark.objects.filter(user=request.user).order_by('-id')
        #page = self.paginate_queryset(queryset)


        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
        try :
            bookmark = Bookmark.objects.get(user=request.user, url=request.data.get('url'))
            return_status = status.HTTP_200_OK
        except :
            serializer = self.serializer_class(data = request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_202_ACCEPTED
                )

            return Response({
                'status': 'Bad request',
                'message': 'Review could not be created with received data.',
                'data' : str(request.data),
                'validated data' : serializer.validated_data,
                'errors' : serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(bookmark)

        return Response(
            serializer.data, status=return_status
        )

    def retrieve(self, request, pk=None):
        queryset = Bookmark.objects.filter(user=request.user)
        bookmark = get_object_or_404(queryset, pk = pk)
        serializer = self.serializer_class(bookmark)
# Call communication : web miner to retrieve title & image
        #webman.retrieveUrlContent(serializer.data)
        #tempCeleryFunction.delay(request=request, bookmark=bookmark, serializer=serializer)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            bookmark = Bookmark.objects.get(pk=pk, user=request.user)
        except Bookmark.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'Bookmark could not be find.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(bookmark, data = request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
# Call communication : web miner to retrieve title & image
            add_info = webman.retrieveUrlContent(serializer.data)
            serializer = self.serializer_class(bookmark, data = add_info, context={'request':request})
            if serializer.is_valid():
                serializer.save()
            else :
                print(serializer.errors)
### finished hack
            return Response(
                serializer.data, status=status.HTTP_202_ACCEPTED
            )

        return Response({
            'status': 'Bad request',
            'message': 'Bookmark could not be updated with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        try:
            bookmark = Bookmark.objects.get(pk=pk, user=request.user)
            bookmark.delete()
        except Bookmark.DoesNotExist:
            return Response({
                'status': 'Not Found',
                'message': 'Bookmark could not be find.'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'Success',
            'message': 'Bookmark deleted'
        }, status=status.HTTP_200_OK)

class PublicBookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(favorite=True) # should be for anonymous users


class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CategorySerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'hook') and self.request.user.hook.active:
            return Category.objects.all()
        else:
            return Category.objects.all()

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, pk=None):
        queryset = Category.objects.all()
        category = get_object_or_404(queryset, pk = pk)

        serializer = self.serializer_class(category)
        return Response(serializer.data)

class KeywordViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

    def perform_create(self, serializer):
        serializer.save()


class FolderViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FolderSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'hook') and self.request.user.hook.active:
            return Folder.objects.all()
        else:
            #return Folder.objects.filter(user=self.request.user)
            #queryset = Folder.objects.filter(authorised_users__id=self.request.user.id)
            queryset = Folder.objects.filter(Q(collaborators__id=self.request.user.id) | Q(owner=self.request.user)).filter(parent=None).distinct()
            queryset = queryset.annotate(bk_count=Count('bookmarks')).order_by('-bk_count')

            return queryset
            #return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    def retrieve(self, request, pk=None):
        queryset = Folder.objects.filter(Q(collaborators__id=self.request.user.id) | Q(owner=self.request.user)).distinct()
        folder = get_object_or_404(queryset, pk = pk)

        serializer = self.serializer_class(folder)
        return Response(serializer.data)


class WebsiteViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WebsiteSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'hook') and self.request.user.hook.active:
            return Website.objects.all()
        else:
            return Website.objects.all()

    def perform_create(self, serializer):
        serializer.save()

class FriendsViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FriendSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'hook') and self.request.user.hook.active:
            return Friend.objects.all()
        else:
            return Friend.objects.filter(from_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

class MeView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request):
        if request.user.is_anonymous:
            return Response({
                'message': 'You are Anonymous',
            }, status=status.HTTP_200_OK)

        serializer = self.serializer_class(request.user, many=False, context= { 'request': request })
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationSerializer

    def get_queryset(self):
        if hasattr(self.request.user, 'hook') and self.request.user.hook.active:
            return Notification.objects.all()
        else:
            return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class query(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        favorite = self.request.query_params.get('favorite', None)
        toread = self.request.query_params.get('toread', None)
        tosort = self.request.query_params.get('tosort', None)
        query = self.request.query_params.get('query', None)
        folder = self.request.query_params.get('folder', None)
        categories = self.request.query_params.get('categories', None)
        category = self.request.query_params.get('category', None)
        wtype = self.request.query_params.get('wtype', None)
        website = self.request.query_params.get('website', None)
        #type = self.request.query_params.get('type', None)
        #folder = self.request.query_params.get('folder', None)

# Start filtering data
        queryset = Bookmark.objects.filter(user=self.request.user, archived=False).order_by('-edit_datetime')
        if toread == "true":
            queryset = queryset.filter(toread=True)
        if favorite == "true":
            queryset = queryset.filter(favorite=True) # limits the search query to bookmarks that are favorites
        #if website is not None:
        #    queryset = queryset.filter(websites__name__startswith=website)
        if categories is not None:
            print("yo here dude")
            try :
                queryset = queryset.filter(categories__id=categories)
                serializer = self.serializer_class(queryset, many=True)
                return Response({ "hits" : serializer.data })
            except :
                queryset = queryset.filter(categories__name__icontains=categories)
                #queryset = queryset.filter(categories__name__icontains=categories)
            #return Response(serializer.data)

        if query is not None:
            # fonction search + sofistiquee avec matrice de mot pour comparaison a la requete
            if len(query.split(" ")) <= 1 :
                returned_queryset = queryset.filter(title__icontains=query) | queryset.filter(description__icontains=query) | queryset.filter(url__icontains=query)
            else :
                query_words = query.split(" ")
                # analyse order of word + word meaning --> matrice of inputted words
                for word in query_words:
                    if len(word) > 0 :
                        word_queryset = queryset.filter(title__icontains=word) | queryset.filter(description__icontains=word) | queryset.filter(url__icontains=word)
                        try :
                            returned_queryset = prev_queryset | word_queryset
                        except :
                            prev_queryset = word_queryset
                            returned_queryset = word_queryset
        else :
            returned_queryset = queryset


        queryset = returned_queryset.distinct() # Precaution
        queryset = queryset.order_by('-edit_datetime', '-added_datetime')
        # !! order by word importance !!!
        data = queryset

        serializer = self.serializer_class(queryset, many=True)
        #return Response(serializer.data)

        return queryset

class Share(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ShareSerializer
    userserz = UserSerializer

    def create(self, request):
        serializer = self.serializer_class(data = request.data, context={'request':request})

        print(request.data)
        if request.data["user"] :
            for user in request.data["user"]:
                new_notification = Notification()
                new_notification.user = User.objects.filter(username=user).first()
                new_notification.notification_type = 'SHARE'
                new_notification.name = request.data["title"]
                new_notification.url = request.data["url"]
                new_notification.save()


        if serializer.is_valid():

            content = library.get_email("share_link", {
                'user': request.user,
                'to': ','.join(serializer.data.get('to')),
                'url': serializer.data.get('url'),
                'title': serializer.data.get('title')
            })
            #postman.send_email(recipient_list=[serializer.data.get('to')], subject=content.subject, html_message=content.html_message)

            return Response(
                serializer.data, status=status.HTTP_202_ACCEPTED
            )

        return Response({
            'status': 'Bad request',
            'message': 'Review could not be created with received data.',
            'data' : str(request.data),
            'validated data' : serializer.validated_data,
            'errors' : serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class Upload(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    bk_serializer_class = BookmarkSerializer
    #serializer_class = ShareSerializer
    #userserz = UserSerializer

    parser = nbp.BookmarkNetscapeHTMLParser()
    def create(self, request):
        error_net = []

        for file in request.data['bookmarkFiles'] :
            ufile = unicode(file, "utf-8")
            self.parser.feed(ufile)

        for bookmark in self.parser.bookmark_list :
            temp_load_obj = dict()
            temp_load_obj['title'] = bookmark['title']
            temp_load_obj['url'] = bookmark['href']
            temp_load_obj['user'] = request.user.id

            try :
                bookmark = Bookmark.objects.get(user=request.user, url=bookmark['href'])
                print('already exists')
            except :
                serializer = self.bk_serializer_class(data = temp_load_obj, context={'request':request})
                if serializer.is_valid():
                    serializer.save()
                else :
                    print(serializer.errors)
                    error_net.append((serializer.errors, serializer.data))

        return Response({
            'imported_bookmarks': self.parser.bookmark_list,
            'imported_folders': self.parser.folder_list,
            'import_errors': error_net
        }
        , status=status.HTTP_202_ACCEPTED
        )
