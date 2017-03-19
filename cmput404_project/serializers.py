from rest_framework import serializers
from .models import Author,Post

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','bio')

class RespondSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=20)
    count = serializers.IntegerField(required=False)
    size = serializers.IntegerField(required=False)
    next = serializers.IntegerField(required=False)
    previous = serializers.IntegerField(required=False)
    #postid = serializers. 
    posts = PostSerializer(many=True,required = False)
    #comments
    #author
    #authors
    #success
    #message
    #friends
    

class PostSerializer(serializers.ModelSerializer):

    author = AuthorSerializer()
    visibility = serializers.SerializerMethodField()
    contentType = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id','visibility','contentType','description','title', 'source', 'origin','author',
        	'content', 'published', 'categories','unlisted')
        
       	read_only_fields = ('id','published','origin','source','author')

    def get_contentType(self,obj):
    	return obj.get_contentType_display()

    def get_visibility(self,obj):
    	return obj.get_visibility_display()
