from django.contrib import admin
from django.contrib.auth.models import User,UserManager
from .models import Profile, Post

admin.site.register(Profile)
admin.site.register(Post)
