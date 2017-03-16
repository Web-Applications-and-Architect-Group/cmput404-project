from django.test import TestCase
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