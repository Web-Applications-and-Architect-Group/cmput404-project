from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404,HttpResponseForbidden
from django.views import View
from django.conf import settings
from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import  Author,Post, friend_request, Comment,Notify,Friend,PostImages,Node
from .forms import ProfileForm,ImageForm,PostForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import sys
import json
import uuid
import requests
import datetime
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import mixins,generics, status, permissions

from .serializers import AuthorSerializer,PostSerializer,CommentSerializer,PostPagination,CommentPagination
from rest_framework.decorators import api_view
from .permissions import IsAuthenticatedNodeOrAdmin
from collections import OrderedDict
from .settings import MAXIMUM_PAGE_SIZE
from .comment_functions import getNodeAuth,getNodeAPIPrefix,friend_relation_validation





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
        # r = requests.get('http://127.0.0.1:8000/service/author/diqiu') # for test
        friend_hostname = request.POST["friend_host"]
        if friend_hostname[len(friend_hostname)-1]=="/":
            friend_hostname = friend_hostname[0:len(friend_hostname)-2]
        # print friend_hostname
        # return
        admin_auth=getNodeAuth(friend_hostname)["auth"] #TODO
        # print(admin_auth)

        r = requests.get(request.POST["friend_url"], auth=admin_auth)
        remote_friend = r.json()
        # print(remote_friend)
        # return

        # get the author on our server
        user = self.get_object(User, request.user.id)
        author = Author.objects.get(user=request.user)
        serializer = AuthorSerializer(author)

        # combines the info
        remote_request = OrderedDict()
        remote_request["query"] = "friendrequest"
        remote_request["author"] = serializer.data
        remote_request["friend"] = remote_friend

        # send friend request to remote server
        # r = requests.post(remote_friend["host"]+'service/friendrequest', data = remote_request)
        r = requests.post(
            remote_friend["host"]+getNodeAPIPrefix(remote_friend["host"])["api_prefix"]+'friendrequest',
            json=remote_request,
            auth=admin_auth
        )

        # store the follow relationship if success
        # print(r.status_code)
        if (r.status_code==200):
            # varify if there is already an exist friend requests
            varify_result = Friend.objects.all()
            varify_result = varify_result.filter(requestee=remote_friend["url"])
            varify_result = varify_result.filter(requestee_id=remote_friend["id"])
            varify_result = varify_result.filter(requester=author)

            if(len(varify_result)<1):
                new_friend = Friend.objects.create(requestee=remote_friend["url"], requestee_id=remote_friend["id"], requester=author)
                new_friend.save()

        # return HttpResponse(json.dumps(serializer.data), status=status.HTTP_200_OK)
        # return HttpResponse(json.dumps(remote_request), status=status.HTTP_200_OK)
        return HttpResponse(r, status=r.status_code)

def update():
    Author.objects.filter(temp=True).delete()
    Post.objects.filter(temp=True).delete()
    Comment.objects.filter(temp=True).delete()
    for node in Node.objects.all():
        r = requests.get(node.host+node.auth_post_url, auth=(node.auth_username, node.auth_password))
        if r.status_code == 200:
            print ("========================")
            print (r.json()['posts'][0])
            print ("=========================")
            serializer = PostSerializer(data=r.json()['posts'],many=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors) 
        else:
            print(r.status_code)

def can_see(post,author):
    if author.url in json.loads(post.visibleTo):
        return True
    if post.visibility == 'PRIVATE' and post.author != author:
        return False
    return True

def prunning(posts,author):
    for post in posts.iterator():
        if not can_see(post,author):
            posts = posts.exclude(id =post.id)
    return posts
        
def home(request):
    update()
    form = PostForm()
    posts= Post.objects.filter(unlisted=False)

    viewer = None
    if(request.user.is_authenticated()):
        viewer = request.user.author
        posts = prunning(posts,viewer)
    else:
        posts = posts.filter(visibility='PUBLIC')
    author = viewer
    
    posts = posts.order_by('-published')

    notify = Notify.objects.filter(requestee=author)
    images = PostImages.objects.all()
    context = { 'posts': posts ,'form': form,'author':author,'Friend_request':notify,'images':images,'viewer':viewer}

    return render(request,'home.html',context)

def stream(request,author_id):
    author = get_object_or_404(Author,pk=author_id)
    posts = Post.objects.filter(author=author).order_by('-published') | Post.objects.filter(visibility=3).order_by('-published')
    form = PostForm()
    visi = None
    images = PostImages.objects.all()
    context = { 'posts': posts ,'author':author,'form':form,'images':images, 'visi':visi}
    return render(request, 'self.html', context)


def profile(request,author_id):
    author = get_object_or_404(Author, pk=author_id)
    viewer = None
    if request.user.is_authenticated:
        viewer = request.user.author
    form = PostForm()
    if request.method == 'POST' and viewer.id == author.id:
        profile_form = ProfileForm(request.POST)
        image_form = ImageForm(request.POST,request.FILES)
        if profile_form.is_valid():
            author.displayName = profile_form.cleaned_data['displayName']
            author.user.email = profile_form.cleaned_data['email']
            author.github = profile_form.cleaned_data['github']
            author.bio = profile_form.cleaned_data['bio']
        else:
            print(profile_form.errors)
        if image_form.is_valid():
            author.img = image_form.cleaned_data['image']
        author.save()
        author.user.save()
    else:
        profile_form = ProfileForm()
    return render(request,'profile/profile.html',{'profile_form':profile_form,'form':form,'viewer':viewer,'author':author})


@login_required
def create_post_html(request):
    return render(request,'post/create_post.html',{'user':request.user})

# with open(settings.MEDIA_ROOT + "/images/" + str(datetime.datetime.now()) +str(count) ,'wb+') as destination:
#     for chunk in f.chunks():
#         destination.write(chunk)

@login_required
def create_post(request):
    """
    Create new post view
    """
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['id'] = uuid.uuid4()
            url = reverse("a_single_post_detail",kwargs={"post_id":data['id']})
            data['origin'] = url
            data['source'] = url
            new_post = Post.objects.create(author=request.user.author,**data)
            
            #https://www.youtube.com/watch?v=C9MDtQHwGYM
            for count,x in enumerate(request.FILES.getlist("files")):
                image = PostImages.objects.create(post=new_post,post_image = x)
                image.save()

        else:
            print(form.errors)
            form = PostForm()
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
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
        else:
            print form.errors
    else:
        form = PostForm(instance=post)
    return HttpResponseRedirect(reverse('onePost',kwargs={'post_id':post_id,'author_id':post.author.id}))

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
    if request.method == "POST":
        author = get_object_or_404(Author,pk=request.user.author.id)
        comment_text = request.POST['comment_text']
        comment_type = request.POST['content_type']
        post_id= request.POST['post_id']
        post = Post.objects.get(id = post_id)

        new_comment = Comment(author, comment_text, post, comment_type)

        host = post.author.host
        if host == HOST_NAME:
            new_comment.save()
        else:
            serializer = AddCommentQuerySerializer(data={'query':'addComment','post':post.origin,'comment':new_comment})
            print serializer.data
    return HttpResponseRedirect(reverse('home'))

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
    notify.delete()
    friend.save()

    notify = Notify.objects.filter(requestee=author)
    context={'user':request.user,'form':PostForm(),'author':author,'Friend_request':notify}
    # return render(request,'friend/friendList.html',context)
    return HttpResponseRedirect(reverse('friendList',kwargs={'author_id': request.user.author.id}))



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


def friendList(request,author_id):
    author = Author.objects.get(pk=author_id)
    friend_requests = author.notify.all()

    viewer = None
    if request.user.is_authenticated:
        viewer = request.user.author

    following_list = author.follow.all()
    following_detail_list = []
    for f_author in following_list:
        # get the authentication of node
        # print(f_author.requester.host)
        admin_auth=getNodeAuth(f_author.requester.host)["auth"]

        # get remote author info thr API
        # print(f_author.requestee, admin_auth)
        # return
        r = requests.get(f_author.requestee, auth=admin_auth)
        if r.status_code==200:
            a_remote_author = OrderedDict()
            a_remote_author = r.json()
        else:
            continue

        friend_validation = friend_relation_validation(author.url, author.host, a_remote_author["url"], a_remote_author["host"])
        if friend_validation["success"] == True and friend_validation["friend_status"] == True:
            a_remote_author["relationship"] = "friend"
        elif friend_validation["success"] == True and friend_validation["friend_status"] == False:
            a_remote_author["relationship"] = "follow"
        else:
            print(friend_validation["messages"])
            continue

        """
        # get remote author's following list
        r = requests.get(f_author.requestee+'/friends', auth=admin_auth)
        if r.status_code==200:
            remote_author_following_list = r.json()
            # print(remote_author_following_list)
            if author_id in remote_author_following_list["authors"]:
                # they are friend
                a_remote_author["relationship"] = "friend"
            else:
                a_remote_author["relationship"] = "follow"
            following_detail_list.append(a_remote_author)
        else:
            continue
        """
        following_detail_list.append(a_remote_author)

    context = {
        'author':author,
        'form':PostForm(),
        'viewer':viewer,
        'friend_requests':friend_requests,
        'following_list':following_detail_list
    }

    #,'Friend':friends,'Followed':follows
    return render(request,'friend/friendList.html',context)

def onePost(request,author_id,post_id):
	post = get_object_or_404(Post,pk = post_id,author=author_id)
	author = get_object_or_404(Author,pk = author_id)
	viewer = None
	if request.user.is_authenticated:
	    viewer = request.user.author
	form = PostForm()
	post.categories = '#'.join(json.loads(post.categories))
	post.visibleTo = ';'.join(json.loads(post.visibleTo))
	context = {'post':post,'author':author,'form':form,'viewer':viewer}
	return render(request,'post/onePost.html',context)
