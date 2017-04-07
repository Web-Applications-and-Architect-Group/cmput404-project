from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins,generics, status, permissions
from .serializers import AuthorSerializer,PostSerializer,CommentSerializer,PostPagination,CommentPagination,AddCommentQuerySerializer
from rest_framework.decorators import api_view
from .permissions import IsAuthenticatedNodeOrAdmin
from collections import OrderedDict
from .settings import MAXIMUM_PAGE_SIZE,HOST_NAME,PROJECT_ROOT
from .models import  Author,Post, friend_request, Comment,Notify,Friend,PostImages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404,get_list_or_404
import uuid,json, requests
from django.http import Http404
from rest_framework.renderers import JSONRenderer
from .comment_functions import getNodeAuth,getNodeAPIPrefix,friend_relation_validation,author_id_parse
import base64
# ============================================= #
# ============= Posts API (START) ============= #
# ============================================= #
def handle_posts(posts,request):
    size = int(request.GET.get('size', MAXIMUM_PAGE_SIZE))
    paginator = PostPagination()
    images = []
    paginator.page_size = size
    result_posts = paginator.paginate_queryset(posts, request)
    for post in result_posts:
        comments = Comment.objects.filter(post=post).order_by('-published')[:5]
        for c in comments.all() :
            c.author.id = c.author.url
        post['comments'] = comments
        post['count'] = comments.count()
        post['size'] = MAXIMUM_PAGE_SIZE
        post['next'] = post.origin + 'comments/'
        post['categories'] = json.loads(post.categories)
        post['visibleTo'] = json.loads(post.visibleTo)
        post['author'].id = post['author'].url

        #============= image
        if post['contentType'] == 'image/png;base64' or post['contentType'] == 'image/jpeg;base64':
            path = PostImages.objects.filter(post=Post.objects.get(id=post['id']))[0].post_image.url
            #post['content'] = base64.b64encode(pimage)
            path = PROJECT_ROOT + path
            fp=open(path,'r+')
            if post['contentType'] == 'image/png;base64':
                post['content'] = "data:image/png;base64, " + base64.b64encode(fp.read())
            if post['contentType'] == 'image/jpeg;base64':
                post['content'] = "data:image/jpeg;base64, " + base64.b64encode(fp.read())
            # fh = open("imageToSave.jpeg", "wb")
            # fh.write(base64.b64decode(post['content']))
            # fh.close()

        #============= image
    serializer = PostSerializer(result_posts, many=True)
        #============= image

        #============= image


    return paginator.get_paginated_response(serializer.data, size)

class Public_Post_List(APIView):
    """
    List all pulic posts
    """
    queryset = Post.objects.filter(visibility='PUBLIC').filter(temp=False)

    def get(self,request,format=None):
        return handle_posts(self.queryset,request)

class Post_Detail(APIView):
    """
    List one post with given post id
    """
    queryset = Post.objects.all()


    def failResponse(self, err_message, status_code):
        # generate fail response
        response = OrderedDict()
        response["query"] = "getPost"
        response["success"] = False
        response["message"] = err_message
        return Response(response, status=status_code)
        # return Response(JSONRenderer().render(response), status=status_code)

    def get(self,request,post_id,format=None):
        posts = get_list_or_404(Post.objects.filter(temp=False),pk=post_id)
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
        post = get_object_or_404(Post.objects.filter(temp=False), pk=post_id)
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
    queryset = Post.objects.exclude(visibility='SERVERONLY').filter(temp=False)

    def get(self,request, format=None):
        return handle_posts(self.queryset,request)

class All_Visible_Post_List_From_An_Author_To_User(APIView):
    """
    List all posts from an author that visible to an authenticated user.
    """
    queryset = Post.objects.exclude(visibility='SERVERONLY').filter(temp=False)

    def get(self,request, author_id, format=None):
        author = get_object_or_404(Author.filter(temp=False),pk=author_id)
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

    def get(self,request,post_id,format=None):
        post = get_object_or_404(Post.objects.filter(temp=False),pk=post_id)
        size = int(request.GET.get('size', 5))
        paginator = CommentPagination()
        paginator.page_size = size

        Comments = Comment.objects.filter(post=post_id)
        result_comments = paginator.paginate_queryset(Comments, request)
        for c in result_comments:
            #post['author'].id = post['author'].url
            c.author.id = c.author.url
        serializer = CommentSerializer(result_comments, many=True)
        return paginator.get_paginated_response(serializer.data, size)

    def post(self,request,post_id,format=None):
        response = OrderedDict()
        response['query'] = 'addComment'
        data = request.data
        serializer = AddCommentQuerySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response['success'] = True
            response['message'] = 'Comment Added'
            code = status.HTTP_200_OK
        else:
            response['success'] = False
            response['message'] = serializer.errors
            code = status.HTTP_400_BAD_REQUEST
        return Response(response,status=code)

# ============ Comments API (END) ============= #





# ============================================= #
# ============ Profile API (START) ============ #
# ============================================= #
class AuthorView(APIView):
    queryset = Author.objects.all()

    def get(self, request, author_id, format=None):
        author1 =  get_object_or_404(Author,pk=author_id)
        serializer = AuthorSerializer(author1)
        author = serializer.data
        author['id'] = author['url']
        author['friends'] = []

        followlist = author1.follow.all()
        for i in followlist :
            serializer = AuthorSerializer(Author.objects.get(id=author_id_parse(i.requestee_id)))
            j = serializer.data
            j['id'] = j['url']
            author['friends'].append(j)

        return Response(author)

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
            if friend.requestee_host == HOST_NAME:
                friend.requestee_host = friend.requestee_host + '/service/'
            if friend.requestee_host[-1] != '/':
                friend.requestee_host = friend.requestee_host + '/'
            print(friend.requestee_id)
            result.append(friend.requestee_host + 'author/' + friend.requestee_id)

        # return success response
        return self.successResponse(HOST_NAME + '/service/author/' + author_id, result)

    def post(self,request, author_id, format=None):
        data = request.data

        # error handling TODOXXX
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

        # pull author info
        try:
            author1 = Author.objects.get(id=author_id1)
        except Author.DoesNotExist:
            response["friends"] = False

        try:
            author2 = Author.objects.get(id=author_id2)
        except Author.DoesNotExist:
            response["friends"] = False

        friend_validation_result = friend_relation_validation(author1.url, author1.host, author2.url, author2.host)
        if friend_validation_result["success"]:
            response["friends"] = friend_validation_result["friend_status"]
            # print "==================="
            # print(response["friends"])
        else:
            response["friends"] = False
            print friend_validation_result["messages"]

        """
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
        """

        # return response
        return Response(response, status=status.HTTP_200_OK)


class Friendrequest_Handler(APIView):
    """
    Handle all friend requests
    """
    queryset = Notify.objects.all()
    def post(self,request,format=None):
        # data = json.loads(request.data)
        data = request.data
        # print(data)
        if not (data["query"] == "friendrequest"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            data["friend"]["id"] = author_id_parse(data["friend"]["id"])
            data["author"]["id"] = author_id_parse(data["author"]["id"])

            friend =  Author.objects.get(id=data["friend"]["id"])

            # redundent Notify check
            varify_result = Notify.objects.all()
            varify_result = varify_result.filter(requester=data["author"]["url"])
            varify_result = varify_result.filter(requester_id = author_id_parse(data["author"]["id"]))
            varify_result = varify_result.filter(requestee=friend)

            # check if requestee have followed requester
            f_varify_result = Friend.objects.all()
            f_varify_result = f_varify_result.filter(requestee=data["author"]["url"])
            f_varify_result = f_varify_result.filter(requestee_id=author_id_parse(data["author"]["id"]))
            f_varify_result = f_varify_result.filter(requester=friend)

            if(len(varify_result)<1 and len(f_varify_result)<1):
                new_notify = Notify.objects.create(requestee=friend,
                                                   requester=data["author"]["url"],
                                                   requester_displayName=data["author"]["displayName"],
                                                   requester_host = data["author"]["host"],
                                                   requester_id = author_id_parse(data["author"]["id"]))
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
