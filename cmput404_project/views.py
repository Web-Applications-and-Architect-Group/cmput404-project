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
    return render(request,'profile/profile.html',{'user':request.user})

@login_required
def profile_edit(request):
    # print >> sys.stderr , request.user.profile
    try:
        print >> sys.stderr , request.user.profile
    except:
        new_profile = Profile(request.user)
        print >> sys.stderr , request.user.profile
    else:
        pass

    return render(request,'profile/profile_edit.html',{'user':request.user})

def profie_update(request, user):
    pass
