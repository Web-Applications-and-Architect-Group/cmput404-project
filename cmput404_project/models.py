from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models.signals import post_save
import uuid
from .settings import HOST_NAME




accept = [
    (0, 'text/plain'),
    (1, 'text/markdown'),
    (2, 'application/base64'),
    (3, 'image/png;base64'),
    (4, 'image/jpeg;base64'),
    (5, 'github-activity'),
    ]


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
        Author.objects.create(user=instance,displayName=instance.username,id=instance.username,url=HOST_NAME+"service/author/"+instance.username);

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

    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visibility = models.IntegerField(choices=authority, default=0)
    contentType = models.IntegerField(choices=accept, default=0)
    description = models.CharField(max_length=100)
    #=================
    title = models.CharField(max_length=50)
    source = models.URLField()
    origin = models.URLField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    published = models.DateTimeField(auto_now =True)
    #categories = models.TextField(null=True)
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

    def __setitem__(self, key, data):
        return setattr(self, key, data)

    def __getitem__(self, key):
        return getattr(self, key)

# Ask if 2 authors are friends
# GET http://service/author/<authorid>/friends/<authorid2>
# STRIP the http:// and https:// from the URI in the restful query
# If you need a template (optional): GET http://service/author/<authorid1>/friends/<service2>/author/<authorid2>
# where authorid1 = de305d54-75b4-431b-adb2-eb6b9e546013 (actually author http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013 )
# where authorid2 =
# GET http://service/author/de305d54-75b4-431b-adb2-eb6b9e546013/friends/127.0.0.1%3A5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891
# responds with:
#{   "query":"friends",
        # Array of Author UUIDs
#        "authors":[
#            "http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
#            "http://127.0.0.1:5454/author/ae345d54-75b4-431b-adb2-fb6b9e547891"
#       ],
#        # boolean true or false
#        "friends": true
#}


@python_2_unicode_compatible
class Friend(models.Model):
    requester = models.ForeignKey(Author,on_delete=models.CASCADE,related_name="follow")
    requestee = models.URLField()

    @classmethod
    def create(cls, requester, requestee):
        new_post = cls(requester=requester, requestee=requestee)
        return new_post

    def __str__(self):
        return self.requester.url


@python_2_unicode_compatible
class Notify(models.Model):
    requestee = models.ForeignKey(Author,on_delete=models.CASCADE,related_name="notify")
    requester = models.URLField()

    @classmethod
    def create(cls, requester, requestee):
        new_post = cls(requester=requester, requestee=requestee)
        return new_post

    def __str__(self):
        return self.requestee.displayName

@python_2_unicode_compatible
class VisibileTo(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="visibileTo")
    visibileTo = models.URLField()
    def __str__(self):
        return self.requestee.username




@python_2_unicode_compatible
class Category(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='categories')
    category = models.CharField(max_length=20)
    def __str__(self):
        return self.category

    def __repr__(self):
        return self.category

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.IntegerField(choices=accept, default=0)
    published = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')

    @classmethod
    def create(cls, user, comment_text, post):
        new_comment = cls(author=user, comment_text=comment_text, post_id=post, comment_date=timezone.now())

        return new_comment

    def __str__(self):

        return self.comment
