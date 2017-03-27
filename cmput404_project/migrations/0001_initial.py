# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-27 21:10
from __future__ import unicode_literals

import cmput404_project.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('img', models.ImageField(default=b'images/defaultUserImage.png', upload_to=b'images/')),
                ('github', models.CharField(blank=True, default=b'', max_length=200)),
                ('bio', models.CharField(blank=True, default=b'', max_length=200)),
                ('is_active', models.BooleanField(default=False)),
                ('host', models.URLField(default=b'https://cloud-dingkai.c9users.io')),
                ('displayName', models.CharField(max_length=200)),
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('temp', models.BooleanField(default=False)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('contentType', models.CharField(choices=[(b'text/plain', b'text/plain'), (b'text/markdown', b'text/markdown'), (b'application/base64', b'application/base64'), (b'image/png; base64', b'image/png;base64'), (b'image/jpeg; base64', b'image/jpeg;base64')], default=b'PUBLIC', max_length=20)),
                ('published', models.DateTimeField(auto_now=True)),
                ('temp', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmput404_project.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requestee', models.URLField()),
                ('requestee_id', models.CharField(max_length=200)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow', to='cmput404_project.Author')),
            ],
        ),
        migrations.CreateModel(
            name='friend_request',
            fields=[
                ('request_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('request_date', models.DateTimeField(verbose_name=b'date published')),
                ('status', models.BooleanField(default=False)),
                ('request_receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('request_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.URLField(unique=True)),
                ('auth_username', models.CharField(max_length=50)),
                ('auth_password', models.CharField(max_length=50)),
                ('public_post_url', models.CharField(default=b'/service/posts?format=json', max_length=50)),
                ('auth_post_url', models.CharField(default=b'/service/author/posts?format=json', max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester', models.URLField()),
                ('requester_displayName', models.CharField(default=b'AuthorName', max_length=30)),
                ('requester_host', models.CharField(default=b'Host', max_length=100)),
                ('requester_id', models.CharField(default=b'id', max_length=200)),
                ('requestee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify', to='cmput404_project.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False)),
                ('visibility', models.CharField(choices=[(b'PUBLIC', b'Public'), (b'FOAF', b'Friend of friend'), (b'FRIENDS', b'Friends'), (b'PRIVATE', b'Private'), (b'SERVERONLY', b'Server Only')], default=b'PUBLIC', max_length=20)),
                ('contentType', models.CharField(choices=[(b'text/plain', b'text/plain'), (b'text/markdown', b'text/markdown'), (b'application/base64', b'application/base64'), (b'image/png; base64', b'image/png;base64'), (b'image/jpeg; base64', b'image/jpeg;base64')], default=b'text/plain', max_length=20)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('title', models.CharField(blank=True, max_length=50)),
                ('source', models.URLField()),
                ('origin', models.URLField()),
                ('content', models.TextField()),
                ('published', models.DateTimeField(auto_now=True)),
                ('unlisted', models.BooleanField(default=False)),
                ('temp', models.BooleanField(default=False)),
                ('visibleTo', models.CharField(blank=True, max_length=100)),
                ('categories', models.CharField(blank=True, max_length=100)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmput404_project.Author')),
            ],
        ),
        migrations.CreateModel(
            name='PostImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_image', models.ImageField(upload_to=cmput404_project.models.content_file_name)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='cmput404_project.Post')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cmput404_project.Post'),
        ),
    ]
