from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.test.utils import setup_test_environment
from cmput404_project.models import Profile, Post, friend_request, Comment
from django.contrib.auth.models import User

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="Bob")
        User.objects.create(username="Dylan")
        User.objects.create(username="Cathy")
    def test_get_friends(self):
        bob = User.objects.get(username="Bob")
        dylan = User.objects.get(username="Dylan")
        cathy = User.objects.get(username="Cathy")
        bob.profile.follows.add(dylan.profile)
        bob.profile.follows.add(cathy.profile)
        dylan.profile.follows.add(cathy.profile)
        dylan.profile.followed_by.add(cathy.profile)
        self.assertEqual(len(bob.profile.get_friends()),0)
        self.assertEqual(len(dylan.profile.get_friends()),1)
        self.assertEqual(len(cathy.profile.get_friends()),1)
        self.assertEqual(dylan.profile.get_friends()[0],cathy.profile)
        self.assertEqual(cathy.profile.get_friends()[0],dylan.profile)

class test_hard_no_more_than(TestCase):

    def set_up(self):
        user = User.objects.create_user(username = 'lily',email= 'ns@gmail.com', password='lily123')
        user.save()

    def test_login(self):
        client = Client()
        response = client.post('/login/', {'username': 'lily', 'password': 'lily123'})
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        self.set_up()
        #user = User.objects.create_user(username = 'lily',email= 'ns@gmail.com', password='lily123')
        #user.save()
        users = User.objects.filter(username="lily")
        self.assertEqual(len(users), 1)

    def test_create_profile(self):
        self.set_up()
        user = User.objects.get(username="lily")
        user.save()

        profile = Profile.create(user)
        profile.github = "github"
        profile.bio = "bio"
        profile.save()

        checkProfile = Profile.objects.filter(user= user, github = "github", bio = "bio")
        self.assertEqual(len(checkProfile), 1)

    def test_view_profile(self):
        self.test_create_profile()
        client = Client()
        client.login(username="lily", password="lily123")
        path = "/profile/"
        response= client.post(path)
        #self.assertEquals(response.context['bio'], "bio")
        #print response
        self.assertEqual(response.status_code, 200)

    def test_edit_profile(self):
        self.test_create_profile()
        client = Client()
        client.login(username="lily", password="lily123")
        path = "/profile/edit"
        forms = {'github': "newGithub", 'bio': "newBio"}
        response= client.post(path,forms)

        self.assertEqual(response.status_code, 200)

    def testPost(self):
        self.set_up()
        user = User.objects.get(username="lily")
        post1 = Post.create(user,"post_text_1","0", "0")
        post2 = Post.create(user,"post_text_2","1", "1")
        post3 = Post.create(user,"post_text_3","4", "0")
        post1.save()
        post2.save()
        post3.save()
        user = User.objects.filter(username="lily")
        allPost = Post.objects.filter(author=user)
        self.assertEqual(len(allPost),3)

    def testStream(self):
        self.test_login()
        self.testPost()
        user = User.objects.filter(username="lily")
        allPost = Post.objects.filter(author=user)
        #self.assertEqual(len(allPost),3)
        url = "/mystream?post_type=my_post&confirm_post= "
        response = self.client.get(url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, 302)
