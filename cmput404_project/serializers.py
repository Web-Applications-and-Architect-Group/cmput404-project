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
        if author.temp:
            serializer = AuthorSerializer(author,data=author_data)
        else:
            return author
    except Author.DoesNotExist:
        author_data['id'] = author_id
        serializer = AuthorSerializer(data=author_data)
    if serializer.is_valid():
        author = serializer.save()
        return author
    else:
        print serializer.errors

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','github','bio')
        extra_kwargs = {
            'id': {'validators':[]},
        }
        
class CommentSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    class Meta:
        model = Comment
        fields = ('author','comment', 'contentType','published','id')
        extra_kwargs = {
            'id': {'validators':[]},
        }




class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    categories = serializers.ListField(child=serializers.CharField(max_length=20),required=False)
    count = serializers.IntegerField(required=False)
    size = serializers.IntegerField(required=False)
    next = serializers.URLField(required=False)
    comments = CommentSerializer(many=True)
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
        categories = json.dumps(validated_data.pop('categories')) if 'categories' in validated_data else '[]'
        visibleTo = json.dumps(validated_data.pop('visibleTo'))  if 'visibleTo' in validated_data else '[]'
        post_id = get_id(validated_data.pop('id'))

        post = Post.objects.create(author=author, id=post_id,temp=True,categories=categories,visibleTo=visibleTo,**validated_data)
        for comment in comments:
            author_data = comment.pop('author')
            author = get_or_create_author(author_data)
            Comment.objects.create(author=author,post=post,**comment)
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
    #post_id = serializers.CharField(max_length=100)

    def create(self,validated_data):
        comment_data = validated_data.pop('comment')
        comment_data['post'] = Post.objects.get(pk=get_id(validated_data.pop('post')))
        author_data = comment_data.pop('author')
        author = get_or_create_author(author_data)
        comment = Comment.objects.create(author=author, **comment_data)
        return comment
    '''
    def validate_post_id(self,value):
        """
        Check that the post_id exist
        """
        try:
            post = Post.objects.get(pk=value)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post with id"+value+" does not exist")
        return value
    '''
    def validate_query(self,value):
        """
        Check that the query is addComment
        """
        if value != 'addComment':
            raise serializers.ValidationError("only accept query addComment")
        return value
