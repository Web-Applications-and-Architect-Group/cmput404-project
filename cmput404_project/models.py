from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
import uuid

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    github = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)

    @classmethod
    def create(cls, user):
        new_profile = cls(user=user)
        return new_profile

    def __str__(self):
        return self.user.username

@python_2_unicode_compatible
class Post(models.Model):
    #================  https://docs.djangoproject.com/en/1.10/ref/models/fields/    idea from this page
    authority = [
        (0, 'Public'),
        (1, 'Friends'),
        (2, 'Friends of friends'),
        (3, 'Private'),
    ]
    can_view = models.IntegerField(choices=authority, default=0)
    #=================
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.CharField(max_length=200)
    pub_datetime = models.DateTimeField('date published')
    #Extra material :  https://docs.djangoproject.com/en/1.10/ref/models/fields/UUIDField
    post_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #=====================
    #image =  models.FileField(default =)
    #======================
	# votes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, post_text,can_view_choice):
        new_post = cls(author=user, post_text=post_text, pub_datetime=timezone.now(), can_view = can_view_choice)
        return new_post
    #def create(cls, user, post_text,can_view_choice,Image):
        #new_post = cls(author=user, post_text=post_text, pub_datetime=timezone.now(), can_view = can_view_choice,Image = image)
        #return new_post

    def __str__(self):
        return self.post_text
