from django.test import TestCase
from cmput404_project.models import Author, Post, Comment, Friend
from django.contrib.auth.models import User

import json
import uuid

"""
Test post
"""
class PostTestCase(TestCase):

    def setUp(self):
        # User and author setUp
        user1 = User.objects.create_user(username="testuser1", password="testpassword1")
        user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        user3 = User.objects.create_user(username="testuser3", password="testpassword3")

        author1 = Author.objects.get(user=user1)
        author2 = Author.objects.get(user=user2)
        author3 = Author.objects.get(user=user3)

        # TODO: friend relationship

        # Post setUp
        post1 = Post.objects.create(author=author1,
                                    content="content1",
                                    title="title1",
                                    visibility="PUBLIC")
        post2 = Post.objects.create(author=author2,
                                    content="content2",
                                    title="title2",
                                    visibility="PUBLIC")
        post3 = Post.objects.create(author=author3,
                                    content="content3",
                                    title="title3",
                                    visibility="PUBLIC")
        post4 = Post.objects.create(author=author1,
                                    content="content4",
                                    title="title4",
                                    visibility="PUBLIC")

    def testGetPostByTitle(self):
        '''
        test if you can get a post by title and
        the information about the post is correct
        '''
        post = Post.objects.filter(title="title1")[0]
        self.assertIsNotNone(post, "Post does not exist")
        self.assertEquals(post.title, "title1", "Title does not match")
        self.assertEquals(post.content, "content1", "Content does not match")
        self.assertEquals(post.visibility, "PUBLIC", "Visibility does not match")

    def testGetAllPosts(self):
        '''
        test if you can get all post you have access to
        '''
        posts = Post.objects.all()
        self.assertEquals(len(posts), 4, "Created 4 post, found " + str(len(posts)))

        for post in posts:
            self.assertIsNotNone(post, "Post is None")

    def testGetAllAuthorPosts(self):
        """
        test if you can get all posts from a certain author
        """
        user = User.objects.get(username="testuser1")
        author = Author.objects.get(user=user)
        posts = Post.objects.filter(author=author)

        self.assertEquals(len(posts), 2, "testuser1 had 2 posts, found " + str(len(posts)))

    def testGetNonExistantPost(self):
        """
        testt if you try to get a non-existant post
        """
        posts = Post.objects.filter(title="NotExist")
        self.assertEquals(len(posts), 0, "Post should not exist!")
