from django.test import TestCase
from cmput404_project.models import Author, Post, Comment, Friend, friend_request
from django.contrib.auth.models import User
from django.utils import timezone
from cmput404_project.views import can_see

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
        #author4 = Author.objects.get(user=user4)
        #author5 = Author.objects.get(user=user5)

        # TODO: friend relationship
        # author1 follows author3
        friend_request.objects.create(request_sender=user1, request_receiver=user3, status=False, request_date=timezone.now())

        # author1 be friend with author2
        friend_request.objects.create(request_sender=user1, request_receiver=user2, status=True, request_date=timezone.now())

        # author2 be friend with author3
        friend_request.objects.create(request_sender=user2, request_receiver=user3, status=True, request_date=timezone.now())

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
        post5 = Post.objects.create(author=author3,
                                    content="content5",
                                    title="title5",
                                    visibility="FRIENDS")


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
        self.assertEquals(len(posts), 5, "Created 5 post, found " + str(len(posts)))

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

    def testDeletePost(self):
        """
        Test if you can delete a post
        """
        user = User.objects.get(username="testuser2")
        author = Author.objects.get(user=user)
        newPost = Post.objects.create(author=author,
                                    title="aNewPost",
                                    content="new post here",
                                    visibility="PUBLIC")

        post = Post.objects.filter(title="aNewPost")[0]
        self.assertIsNotNone(post, "Post should exist!")
        post.delete()
        post2 = Post.objects.filter(title="aNewPost")
        self.assertEquals(len(post2), 0, "Post should not exist")

"""
    def testPostVisibility(self):
        '''
        test post according to user status
        '''
        titles = ["title1", "title2", "title3", "title4", "title5"]
        posts = Post.objects.all()

        # User1 test
        user1 = User.objects.get(username="testuser1")
        author1 = Author.objects.get(user=user1)

        print (author1.url)

        for post in posts:
            #print (post)
            visCheck = can_see(post, author1)
            # author1 should get their own PUBLIC and PRIVATE post (1, 4)
            # author1 is friend with author2, should get their PUBLIC post (post2)
            # author1 is on a visibility exception of post5 (FRIENDs of author3)
            if post!="title5":
                self.assertEqual(visCheck, True)
            else:
                self.assertEqual(visCheck, False)
"""

    def testViewsGetPost(self):
        '''
        test get a single post using the post function in views.py
        '''
        user = User.objects.get(username="testuser1")
        author = Author.objects.get(user=user)
        post = Post.objects.filter(title="title1")[0]
        post_id = post.id

        self.client.login(username="testuser1", password="testpassword1")
        url = "/" + author.id + "/stream"

        response = self.client.post(url)
        #print (response.status_code)
        self.assertEqual(response.status_code, 200,
                        "Post should exist, but response was not 200")
        self.assertIsNotNone(response.context['posts'][0])

    def testViewsDeletePost(self):
        """
        test deleting a post. First creates a new post, then deletes it.
        """
        user = User.objects.get(username="testuser2")
        author = Author.objects.get(user=user)
        newPost = Post.objects.create(author=author,
                                    title="aNewPost",
                                    content="new post here",
                                    visibility="PUBLIC")

        post = Post.objects.filter(title="aNewPost")[0]
        self.assertIsNotNone(post, "Post should exist!")

        post_id = post.id

        self.client.login(username="testuser2", password="testpassword2")
        url = "/" + author.id + "/posts/" + post_id + "/delete_post"

        response = self.client.post(url, {'post_id': post_id})

        self.assertEqual(response.status_code, 302,
                        "Post deletion not successful, code: " +
                        str(response.status_code))

        posts = Post.objects.filter(title="aNewPost");
        self.assertEquals(len(posts), 0, "Post was not successfully deleted")




"""
Test comments
"""
class CommentTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="mockuser1", password="mockpassword")
        user1 = User.objects.get(username="mockuser1")
        author1 = Author.objects.get(user=user1)

        post1 = Post.objects.create(author=author1,
                                    content="content1",
                                    title="title1",
                                    visibility="PUBLIC")
        post2 = Post.objects.create(author=author1,
                                    content="content2",
                                    title="title2",
                                    visibility="PUBLIC")

        Comment.objects.create(author=author1, comment="comment1", post=post1, contentType="text/plain")
        Comment.objects.create(author=author1, comment="comment2", post=post1, contentType="text/plain")
        Comment.objects.create(author=author1, comment="comment3", post=post2, contentType="text/plain")

    def testGetAllComments(self):
        '''
        test if you can get all comments in database
        '''
        comments = Comment.objects.all()
        self.assertEquals(len(comments), 3, "3 comments exist but only " + str(len(comments)) + "found" )

    def testGetComment(self):
        '''
        test if you can get a single comment
        '''
        comment = Comment.objects.filter(comment="comment1")[0]
        self.assertIsNotNone(comment, "Comment exists, but was not found")

        user1 = User.objects.get(username="mockuser1")
        author1 = Author.objects.get(user=user1)
        post1 = Post.objects.filter(title="title1")[0]

        self.assertEquals(comment.author, author1, "Author id does not match")
        self.assertEquals(comment.post, post1, "Post id does not match")
        self.assertEquals(comment.comment, "comment1", "Comment (content) does not match")
        self.assertIsNotNone(comment.published)

    def testGetAllPostComments(self):
        """
        test if you can get all comments from a certain post from the database
        """
        post2 = Post.objects.filter(title="title2")[0]

        comments = Comment.objects.filter(post=post2)
        self.assertEqual(len(comments), 1, "Post has one comment, but " +  str(len(comments)) + " were found")

    def testGetNonExistantComment(self):
        """
        test get a non existant comment from the database
        """
        comments = Comment.objects.filter(comment="dontexist")
        self.assertEquals(len(comments), 0, "Comment should not exist!")

    def testDeleteComment(self):
        """
        test comment deletion from database
        """
        post1 = Post.objects.filter(title="title1")[0]
        user1 = User.objects.get(username="mockuser1")
        author1= Author.objects.get(user=user1)

        Comment.objects.create(author=author1, post=post1, comment="comment4")

        comment = Comment.objects.get(comment="comment4")
        self.assertIsNotNone(comment,"Comment exists, but was not found")

        comment.delete()
        self.assertEquals(len(Comment.objects.filter(comment="comment4")),
                  0, "Comment was not properly deleted")

    def testViewsAddComment(self):
        '''
        test if you can add a comment via comment in views.py
        '''
        self.client.login(username="mockuser1", password="mockpassword")
        user1 = User.objects.get(username="mockuser1")
        #url = "/"
        post1_id = Post.objects.filter(title="title1")[0].id

        '''
        response = self.client.put(url,
                    {'post_id':post1_id,
                         'comment_text':'comment3'})
        print (response.status_code)
        self.assertEqual(response.status_code, 302)
        '''

        #self.assertEqual(comment["comment_text"], "comment3")
        #self.assertEqual(comment["post_id"], str(post1_id))
        #self.assertEqual(comment["author"]["displayname"], "mockuser1")

        # Check it's in the database
        comment = Comment.objects.filter(comment="comment3")[0]
        self.assertIsNotNone(comment, "Comment was not succesfully created")
