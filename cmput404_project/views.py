from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os
from .models import Profile
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

    user = User.objects.get(username = request.user.username)

    return render(request,'profile/profile.html',{'user':request.user})

@login_required
def profile_edit(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except (KeyError, Profile.DoesNotExist):
        print "profile no found create new"
        profile = Profile.create(request.user)
        # profile.save()
    else:
        print profile

    profile.github = "you have changed!"
    profile.save()

    return render(request,'profile/profile_edit.html',{'user':request.user})

def profie_update(request, user):
    pass
