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
from . import views

from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


urlpatterns = [
 	url(r'^', include('registration.backends.simple.urls')),
 	url(r'^profile/$', views.profile, name="profile"),
    url(r'^profile/edit$', views.profile_edit, name="profile_edit"),
    url(r'^profile/update$', views.profile_update, name="profile_update"),
    url(r'^create_post_html$', views.create_post_html, name="create_post_html"),
    url(r'^create_post$', views.create_post, name="create_post"),
    url(r'^view_all_posts$', views.view_all_posts, name="view_all_posts"),
    url(r'^create_post$', views.create_post, name="create_post"),
    url(r'^$', views.home ,name="home"),
    url(r'^admin/', admin.site.urls),
    url(r'^mystream$', views.ViewMyStream, name="ViewMyStream"),
    url(r'^delete_post/$', views.delete_post, name="delete_post"),
    url(r'^comment/$', views.comment, name="comment"),
    url(r'^manage_post/$', views.manage_post, name="manage_post"),
    url(r'^update_post/$', views.update_post, name="update_post"),

]
