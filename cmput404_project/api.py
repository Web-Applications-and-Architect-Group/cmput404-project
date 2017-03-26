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
import uuid,json, requests
from django.http import Http404
from rest_framework.renderers import JSONRenderer

# ============================================= #
# ============= Posts API (START) ============= #
# ============================================= #
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
        post['next'] = post.origin + '/comments'
    serializer = PostSerializer(result_posts, many=True)
    return paginator.get_paginated_response(serializer.data, size)

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

    def failResponse(self, err_message, status_code):
        # generate fail response
        response = OrderedDict()
        response["query"] = "getPost"
        response["success"] = False
        response["message"] = err_message
        return Response(response, status=status_code)
        # return Response(JSONRenderer().render(response), status=status_code)

    def get(self,request,post_id,format=None):
        posts = get_list_or_404(Post,pk=post_id)
        return handle_posts(posts,request)

    def post(self, request, post_id, format=None):
        data = request.data
        # request data fields checking
        try:
            temp_field = data["friends"]
        except KeyError:
            return self.failResponse(
                "Friend list not provided.",
                status.HTTP_400_BAD_REQUEST
            )
        # HOST_NAME

        # error handling
        # if not (data["query"] == "getPost"):
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # if not (data["postid"] == post_id):
        #     return self.failResponse(
        #         "The post id in body is different then the post id in url",
        #         status.HTTP_400_BAD_REQUEST
        #     )

        # get the requested post
        post = get_object_or_404(Post, pk=post_id)
        # get possible FOAF
        post_author_following_list = Friend.objects.filter(requester=post.author)
        possible_middle_friends = post_author_following_list.filter(requestee_id__in=data["friends"])
        # request following list from remote server and compare
        is_FOAF = False
        for middle_friend in possible_middle_friends:
            r = requests.get(middle_friend.requestee+'friends')
            remote_following_list = r.json()
            if post.author.id in remote_following_list:
                is_FOAF = True
                break

        # response
        if is_FOAF:
            posts = get_list_or_404(Post, pk=post_id)
            return handle_posts(posts,request)
        else:
            return self.failResponse(
                "Requester is not FOAF",
                status.HTTP_401_UNAUTHORIZED
            )

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

# ============== Posts API (END) ============== #




# ============================================= #
# =========== Comments API (START) ============ #
# ============================================= #
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
        return Response(response)   # !!!!!!!!!!!!!!!!!!!!!!!!!!!! didn't response with a status code

# ============ Comments API (END) ============= #





# ============================================= #
# ============ Profile API (START) ============ #
# ============================================= #
class AuthorView(APIView):
    queryset = Author.objects.all()
    permission_classes = (IsAuthenticatedNodeOrAdmin,)
    def get(self, request, author_id, format=None):
        author =  get_object_or_404(Author,pk=author_id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

# ============= Profile API (END) ============= #




# ============================================= #
# ============ Friend API (START) ============= #
# ============================================= #

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
                "The author id in body is different then the author id in url",
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


class Accurate_Friend_Inquiry_Handler(APIView):
    """
    handle friend inquiry between two authors.
    """
    queryset = Friend.objects.all()

    def get(self, request, author_id1, author_id2, format=None):
        # prepare response
        response = OrderedDict()
        response["query"] = "friends"
        response["authors"] = [author_id1, author_id2]
        response["friends"] = True

        # pull all the following author by author_id
        following_1 = Friend.objects.filter(requester=author_id1)
        following_2 = Friend.objects.filter(requester=author_id2)

        # two way matches tests, true friend will need to pass both tests
        try:
            following_1.get(requestee_id=author_id2)
        except Friend.DoesNotExist:
            response["friends"] = False

        try:
            following_2.get(requestee_id=author_id1)
        except Friend.DoesNotExist:
            response["friends"] = False

        # return response
        return Response(response, status=status.HTTP_200_OK)


class Friendrequest_Handler(APIView):
    """
    Handle all friend requests
    """
    #TODO get rid of redundent Notify
    queryset = Notify.objects.all()
    def post(self,request,format=None):
        data = request.data
        if not (data["query"] == "friendrequest"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            friend =  Author.objects.get(id=data["friend"]["id"])
            new_notify = Notify.objects.create(requestee=friend,
                                               requester=data["author"]["url"],
                                               requester_displayName=data["author"]["displayName"],
                                               requester_host = data["author"]["host"],
                                               requester_id = data["author"]["id"])
            new_notify.save()
        except Author.DoesNotExist:
            raise Http404
        else:
            response = OrderedDict()
            response["query"] = "friendrequest"
            response["success"] = True
            response["message"] = "Friend request sent"
            return Response(response, status=status.HTTP_200_OK)

# ============= Friend API (END) ============== #