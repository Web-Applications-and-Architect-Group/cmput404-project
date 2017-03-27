from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.test.utils import setup_test_environment
from cmput404_project.models import Profile, Post, friend_request, Comment
from django.contrib.auth.models import User
from .serializers import Postserializer


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

        
class Comments_And_Friends_Test(TestCase):
    
    def set_up(self):
        user = User.objects.create_user(username = 'lily',email= 'ns@gmail.com', password='lily123')
        user.save()
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.author = Author.objects.create(user = self.user, github = 'testUser1.github')
        self.uuid1 = self.author.id
        post1 = Post.create(user,"post_text_1","0", "0")
        post1.save()
        self.user2 = User.objects.create_user(username = 'testUser2', password = 'testUser123')
        self.user2.set_password('testUser456')
        self.user2.is_superuser = True
        self.user2.save()
        self.author2 = Author.objects.create(user = self.user2, github = 'testUser2.github')
        self.uuid2 = self.author2.id
        post2 = Post.create(user,"post_text_2","1", "1")
        post2.save()

    def test_create_comment(self):
        self.client = Client()
        response = self.client.post('/posts/%s/comments/create' % self.post_id, {
            "comment": "here is my first comment",
            "content_type": "text/markdown"
        })
        self.assertEqual(response.status_code, 201)

        #get the id of comment
        self.comment_id = response.data['id']

        # test to get comments
        response = self.client.get('/posts/%s' % self.post_id, {}, format = 'json')
        self.assertEqual(response.status_code, 200)
        comments = response.data['comments']
        self.assertTrue(comments[0]['id'] != None)

        #test to get a comment
        response = self.client.get('/comments/%s' % self.comment_id, {}, format = 'json')
        self.assertEqual(response.status_code, 200)

        #test delete the comment
        response = self.client.delete('/comments/%s/destroy' % self.comment_id)
        self.assertEqual(response.status_code, 204)

    def test_send_friend_request(self):
        self.client = Client()
        #test to send a friend request
        response = self.client.post('/author/friend_request/%s' % self.uuid2, {}, format = 'json')
        self.assertEqual(response.status_code, 202)
        # print self.uid2

        self.client = Client()
        #test get friend request list
        response = self.client.get('/author/friends/friend_requests', {}, format = 'json')
        self.assertEqual(response.status_code, 200)

        #test accept friend request
        response = self.client.post('/author/friend_request/accept/%s' % self.uuid1, {}, format = 'json')
        self.assertEqual(response.status_code, 202)

        #test get friend list for user2, since user1 and user2 are friends now
        response = self.client.get('/author/%s/network' % self.uuid2, {}, format = 'json')
        self.assertEqual(response.status_code, 200)

        #test get all friend's post
        response = self.client.get('/author/%s/posts' % self.uuid1, {}, format = 'json')
        self.assertEqual(response.status_code, 200)

        #test unfriend a friend
        response = self.client.delete('/author/friends/unfriend/%s' % self.uuid1, {}, format = 'json')
        self.assertEqual(response.status_code, 202)

        #test get the friend list for user 2 again,
        response = self.client.get('/author/%s/network' % self.uid2, {}, format = 'json')
        self.assertEqual(response.status_code, 200)
        request = response.data['authors']
        self.assertTrue(request == [])


    def test_reject_friend_requests(self):

        self.client = Client()
        #test to send a friend request
        response = self.client.post('/author/friend_request/%s' % self.uuid2, {}, format = 'json')
        self.assertEqual(response.status_code, 202)

        #test reject friend request
        response = self.client.delete('/author/friend_request/reject/%s' % self.uuid1, {}, format = 'json')
        self.assertEqual(response.status_code, 202)
