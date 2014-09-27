# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend1', '0008_auto_20140813_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='TODOList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('comments', models.TextField(blank=True)),
                ('category', models.CharField(max_length=255, blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TODOListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('todo', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(0, b'not started'), (1, b'started'), (2, b'completed')])),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(related_name=b'+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TODOListSharing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shared_by', models.ForeignKey(related_name=b'shared_with', to=settings.AUTH_USER_MODEL)),
                ('shared_with', models.ForeignKey(related_name=b'shared_by', to=settings.AUTH_USER_MODEL)),
                ('todolist', models.ForeignKey(to='backend1.TODOList')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mood',
            name='moodtype',
        ),
        migrations.RemoveField(
            model_name='mood',
            name='place',
        ),
        migrations.RemoveField(
            model_name='mood',
            name='user',
        ),
        migrations.DeleteModel(
            name='Mood',
        ),
        migrations.DeleteModel(
            name='MoodType',
        ),
        migrations.DeleteModel(
            name='Place',
        ),
        migrations.AlterUniqueTogether(
            name='todolistsharing',
            unique_together=set([('todolist', 'shared_with')]),
        ),
    ]
