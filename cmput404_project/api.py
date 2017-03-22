from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins,generics, status, permissions
from .serializers import AuthorSerializer,PostSerializer,CommentSerializer,PostPagination,CommentPagination,AddCommentQuerySerializer
from rest_framework.decorators import api_view
from .permissions import IsAuthenticatedNodeOrAdmin
from collections import OrderedDict
from .settings import MAXIMUM_PAGE_SIZE
from .models import  Author,Post, friend_request, Comment,Notify,Friend
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404,get_list_or_404
import uuid,json
from django.http import Http404



def handle_posts(posts,request):
    size = int(request.GET.get('size', MAXIMUM_PAGE_SIZE))
    paginator = PostPagination()
    paginator.page_size = size
    result_posts = paginator.paginate_queryset(posts, request)
    for post in result_posts:
        comments = Comment.objects.filter(post=post).order_by('-published')[:5]
        post['comments'] = comments
        post['count'] = comments.count()
        post['size'] = MAXIMUM_PAGE_SIZE
        post['next'] = post['next'] = post.origin + '/comments'
    serializer = PostSerializer(result_posts, many=True)
    return paginator.get_paginated_response(serializer.data, size)

class AuthorView(APIView):
    queryset = Author.objects.all()
    permission_classes = (IsAuthenticatedNodeOrAdmin)
    def get(self, request, pk, format=None):
        author =  get_object_or_404(Author,pk=pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

class Public_Post_List(APIView):
    """
    List all pulic posts
    """
    queryset = Post.objects.filter(visibility=0)
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self,request,format=None):
        return handle_posts(self.queryset,request)
    

class Post_Detail(APIView):

    """
    List one post with given post id
    """
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self,request,post_id,format=None):
        posts = get_list_or_404(Post,pk=post_id)
        return handle_posts(posts,request)

class All_Visible_Post_List_To_User(APIView):
    """
    List all posts that visible to an authenticated user.
    """
    queryset = Post.objects.exclude(visibility=4)
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self,request, format=None):
        return handle_posts(self.queryset,request)
        
class All_Visible_Post_List_From_An_Author_To_User(APIView):
    """
    List all posts from an author that visible to an authenticated user.
    """
    queryset = Post.objects.exclude(visibility=4)
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self,request, author_id, format=None):
        author = get_object_or_404(Author,pk=author_id)
        posts=self.queryset.filter(author = author_id)
        return handle_posts(posts,request)
        


class Comment_list(APIView):

    """
    List all comments, or create a new comment.
    """
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self,request,post_id,format=None):
        post = get_object_or_404(Post,pk=post_id)
        size = int(request.GET.get('size', 5))
        paginator = CommentPagination()
        paginator.page_size = size
        
        Comments = Comment.objects.filter(post=post_id)
        result_comments = paginator.paginate_queryset(Comments, request)

        serializer = CommentSerializer(result_comments, many=True)
        return paginator.get_paginated_response(serializer.data, size)

    def post(self,request,post_id,format=None):
        response = OrderedDict()
        response['query'] = 'addComment'
        data = request.data
        data['post_id'] = post_id
        serializer = AddCommentQuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response['success'] = True
            response['message'] = 'Comment Added'
        else:
            response['success'] = False
            response['message'] = serializer.errors
        return Response(response)

#@api_view(['POST'])
#def handle_friendrequest(request,format=None):
#    queryset = Notify.objects.all()
#    if (request.method == 'POST'):
#        data = request.data
#        if not (data[query] == "friendrequest"):
#            return Response(status=status.HTTP_400_BAD_REQUEST)
#        try:
#            friend =  Author.objects.get(data[friend][id])
#        except Author.DoesNotExist:
#            return Response(status=status.HTTP_400_BAD_REQUEST)
#        new_notify = Notify.objects.create(friend,data[author][url])
#        new_notify.save()

class Friendrequest_Handler(APIView):
    #TODO get rid of redundent Notify
    queryset = Notify.objects.all()
    def post(self,request,format=None):
        data = request.data
        if not (data["query"] == "friendrequest"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            friend =  Author.objects.get(id=data["friend"]["id"])
            new_notify = Notify.objects.create(requestee=friend,requester=data["author"]["url"])
            new_notify.save()
        except Author.DoesNotExist:
            raise Http404
        else:
            response = OrderedDict()
            response["query"] = "friendrequest"
            response["success"] = True
            response["message"] = "Friend request sent"
            return Response(response, status=status.HTTP_200_OK)


class Friend_Inquiry_Handler(APIView):
    """
    return all friends with a given author.
    """
    queryset = Friend.objects.all()

    def successResponse(self, author_id, friend_list):
        # generate success response
        response = OrderedDict()
        response["query"] = "friends"
        response["author"] = author_id
        response["authors"] = friend_list
        return Response(response, status=status.HTTP_200_OK)

    def failResponse(self, err_message, status_code):
        # generate fail response
        response = OrderedDict()
        response["query"] = "friends"
        response["success"] = False,
        response["message"] = err_message
        return Response(response, status=status_code)

    def get(self, request, author_id, format=None):

        # pull all the following author by author_id
        friends = Friend.objects.filter(requester=author_id)

        # store author ids in a list
        result = []
        for friend in friends:
            result.append(friend.requestee_id)

        # return success response
        return self.successResponse(author_id, result)


    def post(self,request, author_id, format=None):
        data = request.data

        # error handling
        if not (data["query"] == "friends"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not (data["author"] == author_id):
            return self.failResponse(
                "author id in body is different then author id in url",
                status.HTTP_400_BAD_REQUEST)

        # proceeds matching
        inquiry_friend_list = data["authors"]
        result = []
        for friend_id in inquiry_friend_list:
            try:
                queryset = Friend.objects.filter(requester=author_id)
                queryset.get(requestee_id=friend_id)
            except Friend.DoesNotExist:
                continue
            else:
                result.append(friend_id)

        # return success response
        return self.successResponse(data["author"], result)