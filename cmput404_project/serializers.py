from rest_framework import serializers,pagination
from .models import Author,Post,Comment
import json
from rest_framework.response import Response
from collections import OrderedDict

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','bio')


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


class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    visibility = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    count = serializers.IntegerField()
    size = serializers.IntegerField()
    next = serializers.URLField()
    comments = CommentSerializer(many=True)
    class Meta:
        model = Post
        fields = ('title','source','origin','description','contentType','content','author','categories','count','size','next','comments','published','id','visibility','visibileTo','unlisted')

    def get_contentType(self,obj):
    	return obj.get_contentType_display()

    def get_visibility(self,obj):
    	return obj.get_visibility_display()
    
    def get_visibileTo(self,obj):
    	result = []
    	for visibileTo in obj.visibileTo.all():
    		result.append(author.visibileTo)
    	return result
    
    def get_categories(self,obj):
    	result = []
    	for category in obj.categories.all():
    		result.append(category.category)
    	return result





class PostPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data, size):
        response = OrderedDict()
        response['query'] = 'posts'
        response['count'] = self.page.paginator.count
        response['size']  = size
        response['posts'] = data

        next_link = self.get_next_link()
        previous_link = self.get_previous_link()
        if (next_link):
            response['next'] = next_link

        if (previous_link):
            response['previous'] = previous_link

        return Response(response)
        