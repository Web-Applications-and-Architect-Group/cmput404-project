from django.contrib import admin
from django.contrib.auth.models import User,UserManager
from .models import Author, Post, friend_request, Comment,Category,Friend,Notify,PostImages

admin.site.register(Author)
admin.site.register(Post)
admin.site.register(friend_request)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Friend)
admin.site.register(Notify)
admin.site.register(PostImages)