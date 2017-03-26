from rest_framework import serializers,pagination
from .models import Author,Post,Comment
import json
from rest_framework.response import Response
from collections import OrderedDict


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','github','bio')
        extra_kwargs = {
            'id': {'validators':[]},
        }
        


class CommentSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    contentType = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('author','comment', 'contentType','published','id')
       	#read_only_fields = ('id','contentType','author')

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

    def create(self,validated_data):
        comment_data = validated_data.pop('comments')
        validated_data.pop('count')
        validated_data.pop('size')
        validated_data.pop('next')
        author_data = validated_data.pop('author')
        try:
            author = Author.objects.get(pk=author_data['id'])
        except Author.DoesNotExist:
            author = Author.objects.create(**author_data)
        post = Post.objects.create(author=author, **validated_data)
        return post
    




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

class CommentPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data, size):
        response = OrderedDict()
        response['query'] = 'comments'
        response['count'] = self.page.paginator.count
        response['size']  = size
        response['comments'] = data

        next_link = self.get_next_link()
        previous_link = self.get_previous_link()
        if (next_link):
            response['next'] = next_link

        if (previous_link):
            response['previous'] = previous_link

        return Response(response)
        
class AddCommentQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=10)
    post = serializers.URLField()
    comment = CommentSerializer()
    post_id = serializers.CharField(max_length=100)
    
    def create(self,validated_data):
        comment_data = validated_data.pop('comment')
        comment_data['post'] = Post.objects.get(pk=validated_data.pop('post_id'))
        author_data = comment_data.pop('author')
        try:
            author = Author.objects.get(pk=author_data['id'])
        except Author.DoesNotExist:
            author = Author.objects.create(**author_data)
        comment = Comment.objects.create(author=author, **comment_data)
        return comment
    
    def validate_post_id(self,value):
        """
        Check that the post_id exist
        """
        try:
            post = Post.objects.get(pk=value)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post with id"+value+" does not exist")
        return value
    
    def validate_query(self,value):
        """
        Check that the query is addComment
        """
        if value != 'addComment':
            raise serializers.ValidationError("only accept query addComment")
        return value
        