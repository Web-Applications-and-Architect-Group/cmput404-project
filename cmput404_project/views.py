from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404,HttpResponseForbidden
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import  Author,Post, friend_request, Comment,Notify,Friend
from .forms import ProfileForm,ImageForm,PostForm
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
from .permissions import IsAuthenticatedNodeOrAdmin
from collections import OrderedDict
from .settings import MAXIMUM_PAGE_SIZE








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

    def post(self,request, author_id, format=None):
        data = request.data

        if not (data["query"] == "friends"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not (data["author"] == author_id):
            return Response({
                "success": False,
                "message":"author id in body is different then author id in url"
            }, status=status.HTTP_400_BAD_REQUEST)

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

        response = data
        response["authors"] = result

        return Response(response, status=status.HTTP_200_OK)


class Send_Friendrequest(LoginRequiredMixin, View):
    """
    send friend request to remote server or our own server
    """
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
            new_friend = Friend.objects.create(requestee=remote_friend["url"], requestee_id=remote_friend["id"], requester=author)
            new_friend.save()

        # return HttpResponse(json.dumps(serializer.data), status=status.HTTP_200_OK)
        # return HttpResponse(json.dumps(remote_request), status=status.HTTP_200_OK)
        return HttpResponse(r, status=r.status_code)








def home(request):
    comments = Comment.objects.all()
    form = PostForm()
    #post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    post= Post.objects.filter(visibility=0).order_by('-published')
    if(request.user):
        try:
            author = Author.objects.get(id=request.user.username)
        except Author.DoesNotExist:
            author=None
    else:
        author = None
    context = { 'posts': post , 'comments': comments,'form': form,'author':author}
    return render(request,'home.html',context)

def selfPage(request):
    comments = Comment.objects.all()

    #post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    post_author = Author.objects.get(id=request.user.username)
    post =Post.objects.filter(author=post_author).order_by('-published')
    if(request.user):
        try:
            author = Author.objects.get(id=request.user.username)
        except Author.DoesNotExist:
            author=None
    else:
        author = None
    form = PostForm()
    context = { 'posts': post , 'comments': comments,'author':author,'form':form}
    return render(request, 'self.html', context)


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



# @login_required
# def create_post(request):
#     """
#     Create new post view
#     """
#     if request.method == "POST":
#         user = User.objects.get(id=request.user.id)
#         visibility = request.POST['post_type']
#         post_text = request.POST['POST_TEXT']
#         post_type = request.POST['content_type']

#         new_post = Post.create(request.user,post_text,can_view, post_type)
#         '''
#         form = ImageForm(request.POST,request.FILES)
#         if form.is_valid():
#             new_post.img = form.cleaned_data['image']
#         '''
#         new_post.save()

#     return HttpResponseRedirect(reverse('profile'))

@login_required
def create_post(request):
    """
    Create new post view
    """
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            author_X = Author.objects.get(user=request.user)
            new_post.author = author_X
            new_post.save()
            new_post.source = "http://http://127.0.0.1:8000/service/posts/%s" %(new_post.id)
            new_post.origin = "http://http://127.0.0.1:8000/service/posts/%s" %(new_post.id)
            new_post.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            form = PostForm()
            return render(request,'/',{'form': form})
    return HttpResponseRedirect(reverse('home'))


@login_required
def manage_post(request):
    """
    post edit view
    """

    post = Post.objects.get(post_id=request.GET['post_id'])

    post_type = request.GET['post_type']

    return render(request,'post/manage_post.html',{'post':post, 'post_type2':post_type})

@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = PostForm(instance=post)
    return render(request,'/',{'form': form})

# @login_required
# def update_post(request):
#     post = Post.objects.get(post_id=request.POST['post_id'])
#     new_post_text = request.POST['post_text']
#     new_can_view = request.POST['post_type']
#     new_post_type = request.POST['content_type']
#     post.post_text = new_post_text
#     post.can_view = new_can_view
#     post.post_type = new_post_type
#     post.save()

#     post_type2 = request.POST['post_type2']
#     # print post_type2
#     context = postContent(post_type2, request)
#     return render(request, 'stream/mystream.html', context)
#     #return HttpResponseRedirect(reverse('ViewMyStream'))

@login_required
def comment(request):
    author = Author.objects.get(displayName = request.user.username)
    comment_text = request.GET['comment_text']
    post_id= request.GET['post_id']
    post = Post.objects.get(id = post_id)

    new_comment = Comment.create(author, comment_text, post)
    new_comment.save()

    #post_type = request.GET['post_type']
    post_type = post.contentType
    context= postContent(post_type,request)

    return render(request, 'home.html', context)
    #return HttpResponseRedirect(reverse('ViewMyStream'), kwargs={'post_type':post_type})

def postContent(post_type,request):
    comments = Comment.objects.all()

    if str(post_type)== "my_post":
            post = Post.objects.filter(author = request.user).order_by('-published')

    elif str(post_type)=="public_post":
        post= Post.objects.filter(visibility=0).order_by('-published')

    elif str(post_type) == "friend_post":
        myFriends= Profile.objects.get(user = request.user).friends.all()
        posts = Post.objects.all()
        post = []
        for friend in myFriends:
            friend_instance= User.objects.get(username=friend)
            friendPost = posts.filter(author = friend_instance)
            for i in friendPost:
                if (i.visibility == 0) or (i.visibility==1):
                    post.append(i)
    else:
        post= Post.objects.filter(visibility=0).order_by('-published')

    context = { 'posts': post , 'comments': comments, 'post_type': post_type}

    return context

@login_required
def ViewMyStream(request):
    Posts = Post.objects.order_by('-published')
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

def friendList(request,username):
	context={'username':username}
	return render(request,'friend/friendList.html',context)

def onePost(request,post_id):
	post = Post.objects.get(id = post_id)
	user = post.author.user
	result = ""
	for category in post.categories.all():
		result += "#"+ category.category + "  "
	context = {'post':post, 'user': user, 'category':result}
	return render(request,'post/onePost.html',context)
