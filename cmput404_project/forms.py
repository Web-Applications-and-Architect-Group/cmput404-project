from django import forms
from django.contrib.auth.forms import AuthenticationForm 

class ImageForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()

class ProfileForm(forms.Form):
    email = forms.EmailField()
    github = forms.CharField(required=False)
    bio = forms.CharField(required=False)
    
