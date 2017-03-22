from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from .models import Post,Comment

class ImageForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()

class ProfileForm(forms.Form):
    displayName = forms.CharField()
    email = forms.EmailField(required=False)
    github = forms.CharField(required=False)
    bio = forms.CharField(required=False)

class PostForm(forms.ModelForm):
	class Meta:
		model=Post
		fields = ['visibility','contentType','description','title','content','unlisted']