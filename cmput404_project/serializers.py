from rest_framework import serializers
from .models import Author,Post,Comment
import json

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','bio')
        read_only_fields=('id','host','url')

class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    visibility = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ('id','visibility','contentType','description','title', 'source', 'origin','author',
        	'content', 'published', 'categories','unlisted')
        
       	read_only_fields = ('id','published','origin','source','author')

    def get_contentType(self,obj):
    	return obj.get_contentType_display()

    def get_visibility(self,obj):
    	return obj.get_visibility_display()

    def get_categories(self,obj):
    	result = []
    	for category in obj.categories.all():
    		result.append(category.category)
    	return result

class CommentSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    contentType = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id','contentType','author',
        	'comment', 'published')
        
       	read_only_fields = ('id','published','origin','source','author')

    def get_contentType(self,obj):
    	return obj.get_contentType_display()

