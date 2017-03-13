from django import forms

class ImageForm(forms.Form):
    """Image upload form."""
    image = forms.ImageField()
 
    