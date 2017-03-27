from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models.signals import post_save
import uuid,json
from .settings import HOST_NAME


accept = [
    ('text/plain', 'text/plain'),
    ('text/markdown', 'text/markdown'),
    ('application/base64', 'application/base64'),
    ('image/png;base64', 'image/png;base64'),
    ('image/jpeg;base64', 'image/jpeg;base64'),
    ]

@python_2_unicode_compatible
class Node(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    host = models.URLField(unique=True)
    auth_username = models.CharField(max_length=50)
    auth_password = models.CharField(max_length=50)
    public_post_url = models.CharField(max_length=50,default="/service/posts?format=json")
    auth_post_url = models.CharField(max_length=50,default="/service/author/posts?format=json")
    def __str__(self):
        return self.host

@python_2_unicode_compatible
class Author(models.Model):
    img = models.ImageField(upload_to= 'images/', default = 'images/defaultUserImage.png')
    github = models.CharField(max_length=200,default="",blank=True)
    bio = models.CharField(max_length=200,default="",blank=True)
    is_active = models.BooleanField(default=False)
    host = models.URLField(default=HOST_NAME)
    displayName = models.CharField(max_length=200)
    id = models.CharField(primary_key=True,max_length=100)
    url = models.URLField()
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='author',blank=True,null=True)
    temp = models.BooleanField(default=False)

    def __str__(self):
        return self.displayName

def create_author(sender,instance,created,**kwargs):
    if created:
        id = uuid.uuid4()
        Author.objects.create(id=id,user=instance,displayName=instance.username,url=HOST_NAME+"/service/author/"+str(id))

post_save.connect(create_author,sender=User)

@python_2_unicode_compatible
class Post(models.Model):
    #================  https://docs.djangoproject.com/en/1.10/ref/models/fields/    idea from this page
    authority = [
        ('PUBLIC', 'Public'),
        ('FOAF', 'Friend of friend'),
        ('FRIENDS', 'Friends'),
        ('PRIVATE', 'Private'),
        ('SERVERONLY', 'Server Only'),
    ]

    id=models.CharField(primary_key=True, default=uuid.uuid4,max_length=100)
    visibility = models.CharField(choices=authority, default='text/plain',max_length=20)
    contentType = models.CharField(choices=accept, default='PUBLIC',max_length=20)
    description = models.CharField(max_length=100,blank=True)
    #=================
    title = models.CharField(max_length=50)
    source = models.URLField()
    origin = models.URLField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    published = models.DateTimeField(auto_now =True)
    #categories = models.TextField(null=True)
    #Extra material :  https://docs.djangoproject.com/en/1.10/ref/models/fields/UUIDField
    unlisted = models.BooleanField(default=False)
    temp = models.BooleanField(default=False)
    visibleTo = models.CharField(max_length=100,blank=True)
    categories = models.CharField(max_length=100,blank=True)
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
    
        
        
        
@python_2_unicode_compatible
class Comment(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4,max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.CharField(choices=accept, default='PUBLIC',max_length=20)
    published = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    temp = models.BooleanField(default=False)
    
    @classmethod
    def create(cls, user, comment_text, post, comment_type):
        new_comment = cls(author=user, comment=comment_text, post=post, contentType=comment_type)

        return new_comment

    def __str__(self):

        return self.comment
    def __setitem__(self, key, data):
        return setattr(self, key, json.dumps(data))

    def __getitem__(self, key):
        return json.loads(getattr(self, key))
        
        
#https://www.youtube.com/watch?v=C9MDtQHwGYM
def content_file_name(instance, filename):
    return '/'.join(['images', str(str(instance.post.id) + filename)])
@python_2_unicode_compatible
class PostImages(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='images')
    post_image = models.ImageField(upload_to=content_file_name)
    def __str__(self):
        return self.post.id




@python_2_unicode_compatible
class Friend(models.Model):
    requester = models.ForeignKey(Author,on_delete=models.CASCADE,related_name="follow")
    requestee = models.URLField()
    requestee_id = models.CharField(max_length=200)

    @classmethod
    def create(cls, requester, requestee, requestee_id):
        new_post = cls(requester=requester, requestee=requestee, requestee_id=requestee_id)
        return new_post

    def __str__(self):
        return self.requester.url


@python_2_unicode_compatible
class Notify(models.Model):
    requestee = models.ForeignKey(Author,on_delete=models.CASCADE,related_name="notify")
    requester = models.URLField()
    requester_displayName = models.CharField(max_length=30,default ="AuthorName")
    requester_host = models.CharField(max_length=100,default="Host")
    requester_id = models.CharField(max_length=200,default="id")
    @classmethod
    def create(cls, requester, requestee):
        new_post = cls(requester=requester, requestee=requestee)
        return new_post

    def __str__(self):
        return self.requestee.displayName



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



