from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404,HttpResponseForbidden
from django.views import View
from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import  Author,Post, friend_request, Comment,Notify,Friend,Category
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
    form = PostForm()
    #post = Post.objects.filter(author = request.user).order_by('-pub_datetime')
    post= Post.objects.filter(visibility=0).order_by('-published')
    author = None
    if(request.user.is_authenticated()):
        author = request.user.author
    context = { 'posts': post ,'form': form,'author':author}
    return render(request,'home.html',context)

def stream(request,author_id):
    author = get_object_or_404(Author,pk=author_id)
    posts = Post.objects.filter(author=author).order_by('-published')
    form = PostForm()
    context = { 'posts': posts ,'author':author,'form':form}
    return render(request, 'self.html', context)


def profile(request,author_id):
    user = get_object_or_404(Author, pk=author_id).user
    viewer = request.user
    form = PostForm()
    if request.method == 'POST' and viewer.id == user.id:
        profile_form = ProfileForm(request.POST)
        image_form = ImageForm(request.POST,request.FILES)
        if profile_form.is_valid():
            user.author.displayName = profile_form.cleaned_data['displayName']
            user.email = profile_form.cleaned_data['email']
            user.author.github = profile_form.cleaned_data['github']
            user.author.bio = profile_form.cleaned_data['bio']
        else:
            print(profile_form.errors)
        if image_form.is_valid():
            user.author.img = image_form.cleaned_data['image']
        user.author.save()
        user.save()
    else:
        profile_form = ProfileForm()
    return render(request,'profile/profile.html',{'profile_form':profile_form,'form':form,'viewer':viewer,'user':user})


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

            #XXX:TODO Category
            cates = request.POST['categoies']
            cate_list = cates.split('#')
            for cate in cate_list:
                m=Category.objects.create(post=new_post,category=cate)
                m.save()

            new_post.source = "http://127.0.0.1:8000/service/posts/%s" %(new_post.id)
            new_post.origin = "http://127.0.0.1:8000/service/posts/%s" %(new_post.id)
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
def update_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        print ("The value of unlisted is :" + request.POST['unlisted'])
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()

            cates = request.POST['category']
            cate_list = cates.split('#')
            print cate_list
            Category.objects.filter(post=post).delete()
            for cate in cate_list:
                if cate.strip() != "":
                    Category.objects.create(post=post,category=cate)



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
    comment_type = request.GET['content_type']
    post_id= request.GET['post_id']
    post = Post.objects.get(id = post_id)

    new_comment = Comment.create(author, comment_text, post, comment_type)
    new_comment.save()

    #post_type = request.GET['post_type']
    post_type = post.contentType
    context= postContent(post_type,request)
    context["author"] = author

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


# @login_required
# def ViewMyStream(request):
#     Posts = Post.objects.order_by('-published')
#     comments = Comment.objects.all()

#     post_type = request.GET['post_type']
#     context = postContent(post_type,request)
#     return render(request, 'stream/user_stream.html', context)

@login_required
def delete_post(request,author_id,post_id):
    post = get_object_or_404(Post,author=author_id,id = post_id)
    if request.user.author.id == author_id:
        post.delete()
    return HttpResponseRedirect(reverse('stream',kwargs={'author_id': author_id}))




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
@login_required
def AcceptFriendRequest(request,requester_id):
    author = Author.objects.get(user=request.user)
    notify = Notify.objects.get(requestee=author,requester_id=requester_id)
    friend = Friend.objects.create(requester=author,requestee=notify.requester,requestee_id = notify.requester_id)
    #notify.delete()
    friend.save()

    notify = Notify.objects.filter(requestee=author)
    context={'user':request.user,'form':PostForm(),'author':author,'Friend_request':notify}
    return render(request,'friend/friendList.html',context)



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
    user = User.objects.get(username=username)
    author = Author.objects.get(user=user)
    notify = Notify.objects.filter(requestee=author)



    context={'user':user,'form':PostForm(),'author':author,'Friend_request':notify}
    #,'Friend':friends,'Followed':follows
    return render(request,'friend/friendList.html',context)

def onePost(request,author_id,post_id):
	post = get_object_or_404(Post,pk = post_id,author=author_id)
	user = Author.objects.get(pk = author_id).user
	result = ""
	for category in post.categories.all():
	    result += "#"+ category.category
	context = {'post':post,'category':result,'user':user}
	return render(request,'post/onePost.html',context)
