from rest_framework import permissions
from django.contrib.auth.models import Group
from .models import Node

#http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user

# only authenticated nodes and admin can use our api
class IsAuthenticatedNodeOrAdmin(permissions.BasePermission):
    def has_permission(self,request,view):
        if request.user.is_staff:
            return True
        try:
            node = Node.objects.get(user=request.user.id)
        except Node.DoesNotExist:
            return False
        return True
        