from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from .models import Profile, Post, Comment
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import sys

'''
def reg_complete(request):
    return render(request, 'registration/registration_complete.html' ,{'what':'Reg Completed!'})
'''

@login_required
def home(request):
    return HttpResponseRedirect(reverse('profile'))

@login_required
def profile(request):
    return render(request,'profile/profile.html',{'user':request.user})

@login_required
def profile_edit(request):
    """
    Profile edit view

    """

    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
        profile.save()
    else:
        print profile

    return render(request,'profile/profile_edit.html',{'user':request.user})


@login_required
def profile_update(request):
    """
    POST handler for profile update

    """

    try:
        profile = Profile.objects.get(user_id=request.user.id)
        user = User.objects.get(id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        # profile no found create new
        profile = Profile.create(request.user)
    else:
        print profile

    user.email = request.POST['user_email']
    user.save()
    profile.github = request.POST['github']
    profile.bio = request.POST['bio']
    profile.save()

    return HttpResponseRedirect(reverse('profile'))

@login_required
def create_post_html(request):
    return render(request,'post/create_post.html',{'user':request.user})

@login_required
def view_all_posts(request):
    Posts = Post.objects.order_by('-pub_datetime')
    comments = Comment.objects.all()
    context = { 'posts': Posts , 'comments': comments}
    #context = { 'posts':Posts}
    return render(request,'post/view_all_posts.html',context)

@login_required
def create_post(request):
    """
    Create new post view

    """

    user = User.objects.get(id=request.user.id)
    can_view = request.POST['post_type']
    post_text = request.POST['POST_TEXT']
    new_post = Post.create(request.user,post_text,can_view)
    #==========
       #image = request.FILES['file']
       #new_post = Post.create(request.user,post_text,can_view,image)
    #=========
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

        
    return render(request,'post/manage_post.html',{'post':post})

@login_required
def update_post(request):
    post = Post.objects.get(post_id=request.POST['post_id'])
    new_post_text = request.POST['post_text']
    new_can_view = request.POST['post_type']
    post.post_text = new_post_text
    post.can_view = new_can_view
    post.save()

    return HttpResponseRedirect(reverse('ViewMyStream'))

@login_required
def comment(request):
    author = User.objects.get(id = request.user.id)
    comment_text = request.POST['comment_text']
    #user = User.objects.get(id=request.user.id)
    post_id= request.POST['post_id']
    post = Post.objects.get(post_id = post_id)

    new_comment = Comment.create(author, comment_text, post)
    new_comment.save()

    return HttpResponseRedirect(reverse('ViewMyStream'))

@login_required
def ViewMyStream(request):
    Posts = Post.objects.order_by('-pub_datetime')
    comments = Comment.objects.all()
    context = { 'posts': Posts , 'comments': comments}

    return render(request, 'stream/mystream.html', context)

@login_required
def delete_post(request):
    myPost = request.GET['post_id']
    allPost = Post.objects.all()
    for i in allPost:
        if (str(i.post_id) == str(myPost)):
            i.delete()
    return HttpResponseRedirect(reverse('ViewMyStream'))

