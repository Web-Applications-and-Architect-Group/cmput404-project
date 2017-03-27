from rest_framework import serializers,pagination
from .models import Author,Post,Comment
import json
from rest_framework.response import Response
from collections import OrderedDict

def get_id(url):
    ids = url.split('/')
    for i in range(len(ids)-1,-1,-1):
        aid = str(ids[i])
        if aid != '':
            break
    return aid

def get_or_create_author(author_data):
    author_id = get_id(author_data.pop('id'))
    try:
        author = Author.objects.get(pk=author_id)
    except Author.DoesNotExist:
        author = Author.objects.create(id=author_id,temp=False,**author_data)
    return author

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
    published = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    class Meta:
        model = Comment
        fields = ('author','comment', 'contentType','published','id')
       	#read_only_fields = ('id','contentType','author')

    def get_contentType(self,obj):
    	return obj.get_contentType_display()



class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    categories = serializers.ListField(child=serializers.CharField(max_length=20))
    count = serializers.IntegerField()
    size = serializers.IntegerField(required=False)
    next = serializers.URLField(required=False)
    comments = CommentSerializer(many=True)
    published = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    visibleTo = serializers.ListField(child=serializers.CharField(max_length=100))
    class Meta:
        model = Post
        fields = ('title','source','origin','description','contentType','content','author','categories','count','size','next','comments','published','id','visibility','visibleTo','unlisted')
        


    def create(self,validated_data):
        comments = validated_data.pop('comments')
        if 'count' in validated_data:
            validated_data.pop('count')
        if 'next' in validated_data:
            validated_data.pop('next')
        if 'size' in validated_data:
            validated_data.pop('size')
        author_data = validated_data.pop('author')
        author = get_or_create_author(author_data)
        categories = json.dumps(validated_data.pop('categories'))
        visibleTo = json.dumps(validated_data.pop('visibleTo'))
        post_id = get_id(validated_data.pop('id'))

        post = Post.objects.create(author=author, id=post_id,temp=True,categories=categories,visibleTo=visibleTo,**validated_data)
        for comment in comments:
            author_data = comment.pop('author')
            author = get_or_create_author(author_data)
            Comment.objects.create(author=author,post=post,temp=True,**comment)
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
