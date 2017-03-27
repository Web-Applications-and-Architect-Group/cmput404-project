from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404,HttpResponseForbidden
from django.views import View
from django.conf import settings
from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from .models import  Author,Post, friend_request, Comment,Notify,Friend,Category,PostImages,Node, VisibleTo
from .forms import ProfileForm,ImageForm,PostForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import sys
import json
import uuid
import requests
import datetime
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import mixins,generics, status, permissions

from .serializers import AuthorSerializer,PostSerializer,CommentSerializer,PostPagination,CommentPagination
from rest_framework.decorators import api_view
from .permissions import IsAuthenticatedNodeOrAdmin
from collections import OrderedDict
from .settings import MAXIMUM_PAGE_SIZE



def getNodeAuth(host_root):
    #TODO
    # try:
    #     node = Node.objects.get(host=host_root)
    # except Node.DoesNotExist:
    #     return {
    #         "success":False,
    #         "messages": "Attempt to connect an untrusted host."
    #     }
    # else:
    #     auth = (node.auth_username, node.auth_password)
    #     return {
    #         "success": True,
    #         "auth": auth
    #     }
    return ("admin", "nimabide")

def getNodeAPIPrefix(host_root):
    # try:
    #     node = Node.objects.get(host=host_root)
    # except Node.DoesNotExist:
    #     return {
    #         "success":False,
    #         "messages": "Attempt to connect an untrusted host."
    #     }
    # else:
    #     api_prefix = node.api_prefix
    #     return {
    #         "success": True,
    #         "api_prefix": api_prefix
    #     }
    return "/service"


"""
Generic function for validating friend relationship status
"""
def friend_relation_validation(friend_url1, friend_host1, friend_url2, friend_host2):
    # greb the Authentication
    node_auth1 = getNodeAuth(friend_host1)
    node_auth2 = getNodeAuth(friend_host2)

    # greb info from urls
    response1 = requests.get(friend_url1, auth=node_auth1)
    response2 = requests.get(friend_url2, auth=node_auth2)

    # validate response from servers
    if response1.status_code==200 and response2.status_code==200:
        author1 = response1.json()
        author2 = response2.json()
    else:
        return {
            "success": False,
            "messages": "A server not response author info properly. \n\
                Server1 status: " + str(response1.status_code) + "\n\
                Server2 status: " + str(response2.status_code)
        }

    try:
        temp_field = author1["id"]
        temp_field = author2["id"]
    except KeyError:
        return {
            "success": False,
            "messages": "A server's author info response has not field [id]."
        }

    # pull following list from both server
    # response1 = requests.get(friend_host1+getNodeAPIPrefix(friend_host1)+"/friends", auth=node_auth1)
    # response2 = requests.get(friend_host2+getNodeAPIPrefix(friend_host2)+"/friends", auth=node_auth2)
    response1 = requests.get(friend_url1+"/friends", auth=node_auth1)
    response2 = requests.get(friend_url2+"/friends", auth=node_auth2)

    # validate the second response from servers
    if response1.status_code==200 and response2.status_code==200:
        author1_following = response1.json()
        author2_following = response2.json()
    else:
        return {
            "success": False,
            "messages": "A server not response following list properly. \n\
                Server1 status: " + str(response1.status_code) + "\n\
                Server2 status: " + str(response2.status_code)
        }

    try:
        temp_field = author1_following["authors"]
        temp_field = author2_following["authors"]
    except KeyError:
        return {
            "success": False,
            "messages": "A server's author following response has not field [authors]."
        }

    # check friend relationship
    if (author1["id"] in author2_following["authors"]) and (author2["id"] in author1_following["authors"]):
        friend_status = True
    else:
        friend_status = False

    return {
        "success": True,
        "friend_status": friend_status
    }
