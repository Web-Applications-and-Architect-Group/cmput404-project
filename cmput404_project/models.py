from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.db.models.signals import post_save
import uuid

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    img = models.ImageField(upload_to= 'images/', default = 'images/defaultUserImage.png')
    github = models.CharField(max_length=200,default="",blank=True)
    bio = models.CharField(max_length=200,default="",blank=True)
    is_active = models.BooleanField(default=False)

    follows = models.ManyToManyField("self", related_name="followed_by", blank=True,symmetrical=False)
    
    def get_friends(self):
        return self.follows.all() & self.followed_by.all()
    
    def get_FOF(self):
        result = self.get_friends()
        friends = list(result)
        for friend in friends:
            result |= friend.get_friends()
        return result
        
    def __str__(self):
        return self.user.username
        
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile,sender=User)
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
        (2, 'image/*')
    ]

    visibility = models.IntegerField(choices=authority, default=0)
    contentType = models.IntegerField(choices=accept, default=0)
    #=================
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.CharField(max_length=200)
    published = models.DateTimeField('date published')
    #Extra material :  https://docs.djangoproject.com/en/1.10/ref/models/fields/UUIDField
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unlisted = models.BooleanField(default=False)
    #=====================
    #image =  models.FileField(default =)
    #======================
	# votes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, post_text,can_view_choice, post_type_choice):
        new_post = cls(author=user, post_text=post_text, pub_datetime=timezone.now(), can_view = can_view_choice, post_type=post_type_choice)
        return new_post

    def __str__(self):
        return self.post_text

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

