from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.CharField(max_length=200)
    pub_datetime = models.DateTimeField('date published')
	# votes = models.IntegerField(default=0)

    @classmethod
    def create(cls, user, post_text):
        new_post = cls(author=user, post_text=post_text, pub_datetime=timezone.now() )
        return new_post

    def __str__(self):
        return self.post_text
