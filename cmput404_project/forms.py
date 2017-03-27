from django import forms
from django.contrib.auth.forms import AuthenticationForm 
from .models import Post,Comment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import json

class ImageForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()
class FileFieldForm(forms.Form):
	file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class ProfileForm(forms.Form):
    displayName = forms.CharField()
    email = forms.EmailField(required=False)
    github = forms.CharField(required=False)
    bio = forms.CharField(required=False)

class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields = ['title','description','categories','contentType','visibility','content','unlisted','visibleTo']
        
    def clean_categories(self):
        data = self.cleaned_data['categories']
        data = filter(lambda a: a != '',data.strip().split('#'))
        data = json.dumps(data)
        return data
    
    def clean_visibleTo(self):
        data = self.cleaned_data['visibleTo']
        data = filter(lambda a: a != '',data.strip().split('#'))
        data = json.dumps(data)
        return data
	    

	
