from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ('id', 'host','displayName','url','bio')
        read_only_fields=('id','host','url')
        