# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-20 06:53
from __future__ import unicode_literals

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
                ('host', models.URLField(default=b'http://127.0.0.1:8000/')),
                ('displayName', models.CharField(max_length=200)),
                ('id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
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
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
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
                ('request_receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('request_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester', models.URLField()),
                ('requestee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notify', to='cmput404_project.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('visibility', models.IntegerField(choices=[(0, b'PUBLIC'), (1, b'FOAF'), (2, b'FRIENDS'), (3, b'PRIVATE'), (4, b'SERVERONLY')], default=0)),
                ('contentType', models.IntegerField(choices=[(0, b'text/plain'), (1, b'text/markdown'), (2, b'application/base64'), (3, b'image/png;base64'), (4, b'image/jpeg;base64'), (5, b'github-activity')], default=0)),
                ('description', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=50)),
                ('source', models.URLField()),
                ('origin', models.URLField()),
                ('content', models.TextField(max_length=200)),
                ('published', models.DateTimeField(auto_now=True)),
                ('unlisted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmput404_project.Author')),
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
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cmput404_project.Post'),
        ),
        migrations.AddField(
            model_name='category',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='cmput404_project.Post'),
        ),
    ]
