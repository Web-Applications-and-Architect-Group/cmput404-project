# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 02:08
from __future__ import unicode_literals

import cmput404_project.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
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
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False)),
                ('comment', models.TextField()),
                ('contentType', models.IntegerField(choices=[(0, b'text/plain'), (1, b'text/markdown'), (2, b'application/base64'), (3, b'image/png;base64'), (4, b'image/jpeg;base64'), (5, b'github-activity')], default=0)),
                ('published', models.DateTimeField(auto_now=True)),
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
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('host', models.URLField()),
                ('auth_username', models.CharField(max_length=50)),
                ('auth_password', models.CharField(max_length=50)),
                ('public_post_url', models.CharField(default=b'/service/posts?format=json', max_length=50)),
                ('auth_post_url', models.CharField(default=b'/service/author/posts?format=json', max_length=50)),
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
                ('visibility', models.IntegerField(choices=[(0, b'PUBLIC'), (1, b'FOAF'), (2, b'FRIENDS'), (3, b'PRIVATE'), (4, b'SERVERONLY')], default=0)),
                ('contentType', models.IntegerField(choices=[(0, b'text/plain'), (1, b'text/markdown'), (2, b'application/base64'), (3, b'image/png;base64'), (4, b'image/jpeg;base64'), (5, b'github-activity')], default=0)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('title', models.CharField(max_length=50)),
                ('source', models.URLField(default=b'https://cloud-dingkai.c9users.io')),
                ('origin', models.URLField(default=b'https://cloud-dingkai.c9users.io')),
                ('content', models.TextField(max_length=200)),
                ('published', models.DateTimeField(auto_now=True)),
                ('unlisted', models.BooleanField(default=False)),
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
        migrations.CreateModel(
            name='VisibileTo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibileTo', models.URLField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visibileTo', to='cmput404_project.Post')),
            ],
        ),
        migrations.AddField(
            model_name='friend_request',
            name='request_receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friend_request',
            name='request_sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cmput404_project.Post'),
        ),
        migrations.AddField(
            model_name='category',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='cmput404_project.Post'),
        ),
        migrations.AddField(
            model_name='author',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
    ]
