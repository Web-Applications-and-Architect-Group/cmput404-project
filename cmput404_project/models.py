from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models.signals import post_save
import uuid
from .settings import HOST_NAME

 
@python_2_unicode_compatible
class Author(models.Model):
    img = models.ImageField(upload_to= 'images/', default = 'images/defaultUserImage.png')
    github = models.CharField(max_length=200,default="",blank=True)
    bio = models.CharField(max_length=200,default="",blank=True)
    is_active = models.BooleanField(default=False)
    host = models.URLField(default=HOST_NAME)
    displayName = models.CharField(max_length=200)
    id = models.CharField(max_length=200,primary_key=True)
    url = models.URLField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='profile')
    

    def __str__(self):
        return self.id
        
def create_author(sender,instance,created,**kwargs):
    if created:
        Author.objects.create(user=instance,displayName=instance.username,id=instance.username,url=HOST_NAME+instance.username);

post_save.connect(create_author,sender=User)

@python_2_unicode_compatible
class Post(models.Model):
    #================  https://docs.djangoproject.com/en/1.10/ref/models/fields/    idea from this page
    authority = [
        (0, 'PUBLIC'),
        (1, 'FOAF'),
        (2, 'FRIENDS'),
        (3, 'PRIVATE'),
        (4, 'SERVERONLY'),
    ]

    accept = [
        (0, 'text/plaintext'),
        (1, 'text/markdown'),
        (2, 'image/*'),
        (3, 'github_activity'),
    ]

    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visibility = models.IntegerField(choices=authority, default=0)
    contentType = models.IntegerField(choices=accept, default=0)
    description = models.CharField(max_length=100)
    #=================
    title = models.CharField(max_length=50)
    source = models.URLField()
    origin = models.URLField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    published = models.DateTimeField(auto_now =True)
    categories = models.TextField(null=True)
    #Extra material :  https://docs.djangoproject.com/en/1.10/ref/models/fields/UUIDField
    unlisted = models.BooleanField(default=False)
    #=====================
    #image =  models.FileField(default =)
    #======================
	# votes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, content,can_view_choice, post_type_choice):
        new_post = cls(author=user, content=content, published=timezone.now(), visibility = can_view_choice, contentType=post_type_choice)
        return new_post

    def __str__(self):
        return self.title

@python_2_unicode_compatible
class friend_request(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_sender = models.ForeignKey(User,related_name="sender",on_delete=models.CASCADE)
    request_receiver = models.ForeignKey(User,related_name="receiver",on_delete=models.CASCADE)
    request_date = models.DateTimeField('date published')
    status = models.BooleanField(default=False)

    @classmethod
    def create(cls ,request_sender,request_receiver,status):
        new_request = cls(request_sender=request_sender,request_receiver=request_receiver,status=status,request_date=timezone.now())
        return new_request

    def __str__(self):
        return self.request_sender.username


@python_2_unicode_compatible
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=1000)
    comment_date = models.DateTimeField('date commented')
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, db_column='post_id', default='', editable='False')

    @classmethod
    def create(cls, user, comment_text, post):
        new_comment = cls(author=user, comment_text=comment_text, post_id=post, comment_date=timezone.now())

        return new_comment

    def __str__(self):
        return self.comment_text

