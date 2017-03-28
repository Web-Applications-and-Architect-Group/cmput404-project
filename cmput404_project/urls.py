"""cmput404_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from . import views,api
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    ### (START) API specify by
    # https://github.com/Web-Applications-and-Architect-Group/CMPUT404-project-socialdistribution/blob/master/example-article.json
    # --------------------------------
    # """
    # Posts API (part 1)
    # """
    url(r'^service/author/posts$',
        api.All_Visible_Post_List_To_User.as_view(),
        name='authenticated_user_visible_post_list'),               # Allow [GET]. GET Done

    # """
    # Profile API
    # """
    url(r'^service/author/(?P<author_id>[a-zA-Z0-9-_]+)$',          # Allow [GET]. GET partial Done TODO should contain friend list as well
        api.AuthorView.as_view(), name='author_profile'),

    # """
    # Posts API (part 2)
    # """
    url(r'^service/posts/$',
        api.Public_Post_List.as_view(), name='public_post_list'),   # Allow [GET]. GET Done
    url(r'^service/posts/(?P<post_id>[a-zA-Z0-9-_]+)$',
        api.Post_Detail.as_view(),name='a_single_post_detail'),     # Allow [GET, POST]. GET, POST Done
    url(r'^service/author/(?P<author_id>[a-zA-Z0-9-_]+)/posts$',
        api.All_Visible_Post_List_From_An_Author_To_User.as_view(),
        name='authenticated_user_visible_post_list_from_an_author'),# Allow [GET]. GET Done

    # """
    # Comments API
    # """
    url(r'^service/posts/(?P<post_id>[a-zA-Z0-9-_]+)/comments$',
        api.Comment_list.as_view(),name='comments_in_a_post'),      # Allow [GET, POST] Done

    # """
    # Friend API
    # """
    url(r'^service/author/(?P<author_id>[a-zA-Z0-9-_]+)/friends/$',  # Allow [GET, POST]. GET, POST Done
        api.Friend_Inquiry_Handler.as_view(), name='friend_inquiry'),
    url(r'^service/author/(?P<author_id1>[a-zA-Z0-9-_]+)/friends/(?P<author_id2>[a-zA-Z0-9-_]+)$',
        api.Accurate_Friend_Inquiry_Handler.as_view(),
        name='friend_inquiry_by_ids'),                              # Allow [GET]. GET done
    # url(r'^service/author/(?P<author_id1>[a-zA-Z0-9-_]+)/friends/<service2>/author/(?P<author_id2>[a-zA-Z0-9-_]+)$',
    #     views.Post_list.as_view(), name='friend_inquiry_by_ids'), #TODO? Optional
    url(r'^service/friendrequest/$',                                         # Allow [POST]. POST Done
        api.Friendrequest_Handler.as_view(), name="make_friendrequest"),

    ### (END) API specify by
    # https://github.com/Web-Applications-and-Architect-Group/CMPUT404-project-socialdistribution/blob/master/example-article.json
    # --------------------------------
    url(r'^admin/', admin.site.urls),
    url(r'^', include('registration.backends.simple.urls')),
    url(r'^(?P<author_id>[a-zA-Z0-9-_]+)/profile$', views.profile, name="profile"),
    url(r'^(?P<author_id>[a-zA-Z0-9-_]+)/friendList$', views.friendList, name="friendList"),
    #url(r'^onePost',views.onePost, name="onePost"),
    url(r'^(?P<author_id>[a-zA-Z0-9-_]+)/posts/(?P<post_id>[a-zA-Z0-9-]+)$', views.onePost, name="onePost"),

    #url(r'^friendList', views.friendList, name="friendList"),

    url(r'^send_friendrequest$',views.Send_Friendrequest.as_view(),name='send_friendrequest'),  # TODO need to add authetication
    #url(r'^view_profile/(?P<username>[a-zA-Z0-9]+)$', views.view_profile, name="view_profile"),


    # url(r'^friendrequest$', views.handle_friendrequest.as_view(), name="make_friendrequest"),
    url(r'^(?P<author_id>[a-zA-Z0-9-_]+)/stream$', views.stream, name="stream"),
    url(r'^create_post_html$', views.create_post_html, name="create_post_html"),
    url(r'^create_post$', views.create_post, name="create_post"),
    url(r'^$', views.home ,name="home"),

    #url(r'^mystream$', views.ViewMyStream, name="ViewMyStream"),
    url(r'^(?P<author_id>[a-zA-Z0-9-_]+)/posts/(?P<post_id>[a-zA-Z0-9-_]+)/delete_post$', views.delete_post, name="delete_post"),
    url(r'^comment$', views.comment, name="comment"),
    url(r'^manage_post$', views.manage_post, name="manage_post"),
    url(r'^(?P<post_id>[a-zA-Z0-9-]+)/update_post$', views.update_post, name="update_post"),
    url(r'^Add_friend$', views.Add_friend, name="Add_friend"),
    #url(r'^accept_friend$', views.accept_friend, name="accept_friend"),
    url(r'^AcceptFriendRequest/(?P<requester_id>[a-zA-z0-9-_]+)$', views.AcceptFriendRequest, name="AcceptFriendRequest"),
    url(r'^api_list_my_friend_request$', views.list_my_friend_request, name="list_my_friend_request"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
urlpatterns = format_suffix_patterns(urlpatterns)

#http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
