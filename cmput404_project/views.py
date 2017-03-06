from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from .models import Profile, Post
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
def create_post(request):
    """
    Create new post view

    """
    post_text = request.POST['POST_TEXT']
    new_post = Post.create(request.user,post_text)
    new_post.save()

    return HttpResponseRedirect(reverse('profile'))
