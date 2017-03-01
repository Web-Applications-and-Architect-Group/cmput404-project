from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.ForeignKey(User)
    github = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)
    def __str__(self):
        return self.user.username