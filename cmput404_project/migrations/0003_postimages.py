# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-26 00:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmput404_project', '0002_auto_20170325_2105'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_image', models.ImageField(upload_to=b'')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='cmput404_project.Post')),
            ],
        ),
    ]