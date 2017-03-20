from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import  Author,Post, friend_request, Comment,Notify,Friend
from .forms import ProfileForm,ImageForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import sys
import json
import uuid
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins,generics, status, permissions
from .serializers import AuthorSerializer,PostSerializer,CommentSerializer,PostPagination,CommentPagination
from rest_framework.decorators import api_view
from .permissions import IsOwnerOrReadOnly
from collections import OrderedDict

class AuthorView(APIView):
    queryset = Author.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly,)
    def get_object(self, pk):
        try:
            author =  Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            raise Http404
        return author

    def get(self, request, pk, format=None):
        print(format)
        author = self.get_object(pk)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    def post(self,request,pk,format=None):
        author = self.get_object(pk)
        serializer = AuthorSerializer(author,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk,format=None):
        return self.post(request,pk,format)



def home(request):
    comments = Comment.objects.all()

    #post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    post= Post.objects.filter(visibility=0).order_by('published')
    context = { 'posts': post , 'comments': comments}
    return render(request,'home.html',context)

def selfPage(request):
    comments = Comment.objects.all()

    #post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    post =Post.objects.all()

    context = { 'posts': post , 'comments': comments}
    return render(request, 'self.html', context)

class Post_list(APIView):

    """
    List all posts, or create a new post.
    """
    queryset = Post.objects.filter(visibility=0)

    def get(self,request,format=None):
        size = int(request.GET.get('size', 1))
        paginator = PostPagination()
        paginator.page_size = size
        posts = self.queryset
        result_posts = paginator.paginate_queryset(posts, request)
        for post in result_posts:
            comments = Comment.objects.filter(post=post).order_by('-published')[:5]
            post['comments'] = comments
            post['count'] = comments.count()
            post['size'] = size
            post['next'] = post.origin + 'service/posts/' + str(post.id) + '/comments'
        serializer = PostSerializer(result_posts, many=True)
        return paginator.get_paginated_response(serializer.data, size)

    def post(self,request,format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class All_Visible_Post_List_From_An_Author_To_User(APIView):
    """
    List all posts from an author that visible to an authenticated user.
    """
    queryset = Post.objects.all()

    def get(self,request, author_id, format=None):
        size = int(request.GET.get('size', 1))
        paginator = PostPagination()
        paginator.page_size = size

        """
        author = Author.objects.get(pk=author_id)
        all_posts = Post.objects.filter(author=author)
        #TODO check if they are friend
        is_friend = False
        is_FOAF = False
        if (is_friend):
            posts = all_posts.filter(visibility=0, visibility=1, visibility=2)
        elif (is_FOAF):
            posts = all_posts.filter(visibility=0, visibility=2)
        else:
            posts = all_posts.filter(visibility=0)
        """

        result_posts = paginator.paginate_queryset(posts, request)
        for post in result_posts:
            comments = Comment.objects.filter(post=post).order_by('-published')[:5]
            post['comments'] = comments
            post['count'] = comments.count()
            post['size'] = size
            post['next'] = post.origin + 'service/posts/' + str(post.id) + '/comments'
        serializer = PostSerializer(result_posts, many=True)
        return paginator.get_paginated_response(serializer.data, size)

class All_Visible_Post_List_To_User(APIView):
    """
    List all posts from an author that visible to an authenticated user.
    """
    queryset = Post.objects.all()

    def get(self,request, format=None):
        size = int(request.GET.get('size', 1))
        paginator = PostPagination()
        paginator.page_size = size

        """
        myself_user = User.objects.get(pk=request.user.id)
        myself = Author.objects.get(pk=myself_user)
        author = Author.objects.get(pk=author_id)
        all_posts = Post.objects.filter(author=author)
        #TODO check if they are friend one by one
        is_friend = False
        is_FOAF = False
        if (is_friend):
            posts = all_posts.filter(visibility=0, visibility=1, visibility=2)
        elif (is_FOAF):
            posts = all_posts.filter(visibility=0, visibility=2)
        else:
            posts = all_posts.filter(visibility=0)
        """

        result_posts = paginator.paginate_queryset(posts, request)
        for post in result_posts:
            comments = Comment.objects.filter(post=post).order_by('-published')[:5]
            post['comments'] = comments
            post['count'] = comments.count()
            post['size'] = size
            post['next'] = post.origin + 'service/posts/' + str(post.id) + '/comments'
        serializer = PostSerializer(result_posts, many=True)
        return paginator.get_paginated_response(serializer.data, size)

class Post_detail(APIView):

    """
    List single posts, or create a new post.
    """
    queryset = Post.objects.all()
    def get_object(self, pk):
        try:
            post =  Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
        return post

    def get(self,request,post_id,format=None):
        size = 1
        paginator = PostPagination()
        paginator.page_size = size
        posts = Post.objects.filter(pk=post_id)
        result_posts = paginator.paginate_queryset(posts, request)
        for post in result_posts:
            comments = Comment.objects.filter(post=post).order_by('-published')[:5]
            post['comments'] = comments
            post['count'] = comments.count()
            post['size'] = size
            post['next'] = post.origin + 'service/posts/' + str(post.id) + '/comments'
        serializer = PostSerializer(result_posts, many=True)
        return paginator.get_paginated_response(serializer.data, size)
        # Post = self.get_object(pk)
        # serializer = PostSerializer(Post)
        # return Response(serializer.data)
    def post(self,request,pk,format=None):
        Post = Post.objects.get(pk)
        serializer = PostSerializer(Post,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self,request,pk,format=None):

        return self.post(request,pk,format)


class Comment_list(APIView):

    """
    List all comments, or create a new comment.
    """
    queryset = Comment.objects.all()
    def get_object(self, pk):
        try:
            post =  Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
        return post

    def get(self,request,post_id,format=None):
        post = self.get_object(post_id)

        size = int(request.GET.get('size', 5))
        paginator = CommentPagination()
        paginator.page_size = size

        Comments = Comment.objects.filter(post=post_id)
        result_comments = paginator.paginate_queryset(Comments, request)

        serializer = CommentSerializer(result_comments, many=True)
        return paginator.get_paginated_response(serializer.data, size)
        # Comments = self.get_object(pk)
        # serializer = CommentSerializer(result_posts,many=True)
        # return Response(serializer.data)
    def post(self,request,format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

class handle_friendrequest(APIView):
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


class Send_Friendrequest(LoginRequiredMixin, View):
    queryset = Notify.objects.all()

    def get_object(self, model, pk):
        try:
            result =  model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404
        return result

    def post(self, request):
        # get the friend on remote server
        r = requests.get('http://127.0.0.1:8000/service/author/diqiu') # for test
        # r = requests.get(request.friend_url)
        remote_friend = r.json()

        # get the author on our server
        user = self.get_object(User, request.user.id)
        author = Author.objects.get(id=user.username)
        serializer = AuthorSerializer(author)

        # combines the info
        remote_request = OrderedDict()
        remote_request["query"] = "friendrequest"
        remote_request["author"] = serializer.data
        remote_request["friend"] = r.json()

        # send friend request to remote server
        # r = requests.post(remote_friend["host"]+'service/friendrequest', data = remote_request)
        r = requests.post(remote_friend["host"]+'service/friendrequest', data = remote_request)

        # store the follow relationship if success
        # print(r.status_code)
        if (r.status_code==200):
            new_friend = Notify.objects.create(requestee=remote_friend["url"],requester=author)
            new_friend.save()

        # return HttpResponse(json.dumps(serializer.data), status=status.HTTP_200_OK)
        # return HttpResponse(json.dumps(remote_request), status=status.HTTP_200_OK)
        return HttpResponse(r, status=r.status_code)









@login_required
def profile(request,username):
    user = get_object_or_404(User, username=username)
    viewer = request.user
    if request.method == 'POST' and viewer.id == user.id:
        profile_form = ProfileForm(request.POST)
        image_form = ImageForm(request.POST,request.FILES)
        if profile_form.is_valid():
            user.email = profile_form.cleaned_data['email']
            user.profile.github = profile_form.cleaned_data['github']
            user.profile.bio = profile_form.cleaned_data['bio']
        else:
            print(profile_form.errors)
        if image_form.is_valid():
            user.profile.img = image_form.cleaned_data['image']
        user.profile.save()
        user.save()
    else:
        profile_form = ProfileForm()
    return render(request,'profile/profile.html',{'profile_form':profile_form,'viewer':viewer,'user':user})


def profile_old(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
        user = User.objects.get(id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
        profile.save()
    else:
        # print profile
        pass

    friend_requests = friend_request.objects.filter(request_receiver=request.user)

    friends = Profile.objects.get(user=request.user).friends.all()
    # print (friends)
    return render(request,'profile/profile_old.html',{'user':request.user, 'request_by':request.user,
        'friend_list':friends,'friend_request':friend_requests})
@login_required
def create_post_html(request):
    return render(request,'post/create_post.html',{'user':request.user})



@login_required
def create_post(request):
    """
    Create new post view
    """
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        visibility = request.POST['post_type']
        post_text = request.POST['POST_TEXT']
        post_type = request.POST['content_type']

        new_post = Post.create(request.user,post_text,can_view, post_type)
        '''
        form = ImageForm(request.POST,request.FILES)
        if form.is_valid():
            new_post.img = form.cleaned_data['image']
        '''
        new_post.save()

    return HttpResponseRedirect(reverse('profile'))

    # new_post = Post.create(request.user,"a new one")
    # new_post.save()

    # return HttpResponseRedirect(reverse('profile'))
@login_required
def manage_post(request):
    """
    post edit view
    """

    post = Post.objects.get(post_id=request.GET['post_id'])

    post_type = request.GET['post_type']

    return render(request,'post/manage_post.html',{'post':post, 'post_type2':post_type})


@login_required
def update_post(request):
    post = Post.objects.get(post_id=request.POST['post_id'])
    new_post_text = request.POST['post_text']
    new_can_view = request.POST['post_type']
    new_post_type = request.POST['content_type']
    post.post_text = new_post_text
    post.can_view = new_can_view
    post.post_type = new_post_type
    post.save()

    post_type2 = request.POST['post_type2']
    # print post_type2
    context = postContent(post_type2, request)
    return render(request, 'stream/mystream.html', context)
    #return HttpResponseRedirect(reverse('ViewMyStream'))

@login_required
def comment(request):
    author = User.objects.get(id = request.user.id)
    comment_text = request.GET['comment_text']
    post_id= request.GET['post_id']
    post = Post.objects.get(post_id = post_id)

    new_comment = Comment.create(author, comment_text, post)
    new_comment.save()

    post_type = request.GET['post_type']
    context= postContent(post_type,request)

    return render(request, 'stream/mystream.html', context)
    #return HttpResponseRedirect(reverse('ViewMyStream'), kwargs={'post_type':post_type})

def postContent(post_type,request):
    comments = Comment.objects.all()

    if str(post_type)== "my_post":
            post = Post.objects.filter(author = request.user).order_by('-pub_datetime')

    elif str(post_type)=="public_post":
        post= Post.objects.filter(can_view=0).order_by('-pub_datetime')

    elif str(post_type) == "friend_post":
        myFriends= Profile.objects.get(user = request.user).friends.all()
        posts = Post.objects.all()
        post = []
        for friend in myFriends:
            friend_instance= User.objects.get(username=friend)
            friendPost = posts.filter(author = friend_instance)
            for i in friendPost:
                if (i.can_view == 0) or (i.can_view==1):
                    post.append(i)
    else:
        post= Post.objects.filter(can_view=0).order_by('-pub_datetime')

    context = { 'posts': post , 'comments': comments, 'post_type': post_type}

    return context

@login_required
def ViewMyStream(request):
    Posts = Post.objects.order_by('-pub_datetime')
    comments = Comment.objects.all()

    post_type = request.GET['post_type']
    context = postContent(post_type,request)
    return render(request, 'stream/user_stream.html', context)

@login_required
def delete_post(request):
    myPost = request.GET['post_id']
    allPost = Post.objects.all()
    for i in allPost:
        if (str(i.post_id) == str(myPost)):
            i.delete()
    #return HttpResponseRedirect(reverse('ViewMyStream'))
    post_type = request.GET['post_type']
    context = postContent(post_type,request)
    return render(request, 'stream/mystream.html', context)


@login_required
def Add_friend(request):
    request_sender_id = request.POST['request_sender']
    request_receiver_id = request.POST['request_receiver']
    request_sender = User.objects.get(id=request_sender_id)
    request_receiver = User.objects.get(id=request_receiver_id)
    status = False
    new_request = friend_request.create(request_sender,request_receiver,status)
    new_request.save()


    return HttpResponseRedirect(reverse('profile'))
@login_required
def list_my_friend_request(request):
    friend_requests = friend_request.objects.get(request_receiver=request.user)
    #friend_requests = friend_request.objects.all()

    return JsonResponse(friend_requests,safe=False)

@login_required
def accept_friend(request):
    request_f = friend_request.objects.get(request_id=request.POST['request_id'])
    request_f.status = True
    request_f.save()
    profile_for_requester = Profile.objects.get(user=request_f.request_sender)
    profile_for_requestee = Profile.objects.get(user=request_f.request_receiver)
    profile_for_requester.friends.add(profile_for_requestee)
    profile_for_requestee.friends.add(profile_for_requester)
    profile_for_requester.save()
    profile_for_requestee.save()
    #profile.friends.add(request.request_sender)



    return HttpResponseRedirect(reverse('profile'))


def viewUnlistedPost(request, post_id):
    post = get_object_by_uuid_or_404(Post, post_id)

    # post_id = request.GET['post_id']
    unlistedPost = Post.objects.get(pk=post_id)
    context = { 'post': unlistedPost }

    return render(request, 'post/shared_post.html', context)

### reference by: http://brainstorm.it/snippets/get_object_or_404-for-uuids/
def get_object_by_uuid_or_404(model, uuid_pk):
    """
    Calls get_object_or_404(model, pk=uuid_pk)
    but also prevents "badly formed hexadecimal UUID string" unhandled exception
    """
    try:
        uuid.UUID(uuid_pk)
    except Exception, e:
        raise Http404(str(e))
    return get_object_or_404(model, pk=uuid_pk)
