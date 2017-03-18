from rest_framework import serializers
from .models import Author,Post

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','bio')
        #read_only_fields=('id','host','url')
class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id','visibility','contentType','description','title', 'source', 'origin','author',
        	'content', 'published', 'categories','unlisted')