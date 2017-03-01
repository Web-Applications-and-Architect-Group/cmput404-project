from django.contrib import admin
from django.contrib.auth.models import User,UserManager
from .models import Profile

admin.site.register(Profile)
