# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('backend1', '0013_auto_20140910_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='todolist',
            name='date_created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolist',
            name='date_updated',
            field=django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolist',
            name='rname',
            field=models.CharField(default=b'(no rname)', help_text=b'Internal object name (fit for admin/backend tasks only)', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='date_created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='date_updated',
            field=django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='rname',
            field=models.CharField(default=b'(no rname)', help_text=b'Internal object name (fit for admin/backend tasks only)', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistsharing',
            name='date_created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistsharing',
            name='date_updated',
            field=django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistsharing',
            name='rname',
            field=models.CharField(default=b'(no rname)', help_text=b'Internal object name (fit for admin/backend tasks only)', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='todolist',
            name='created_by',
            field=models.ForeignKey(to='backend1.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='todolistitem',
            name='created_by',
            field=models.ForeignKey(related_name=b'+', to='backend1.UserProfile'),
        ),
        migrations.AlterField(
            model_name='todolistitem',
            name='last_updated_by',
            field=models.ForeignKey(related_name=b'+', to='backend1.UserProfile', null=True),
        ),
        migrations.AlterField(
            model_name='todolistitem',
            name='todolist',
            field=models.ForeignKey(related_name=b'todolistitems', to='backend1.TODOList'),
        ),
        migrations.AlterField(
            model_name='todolistsharing',
            name='shared_by',
            field=models.ForeignKey(related_name=b'shared_with', to='backend1.UserProfile'),
        ),
        migrations.AlterField(
            model_name='todolistsharing',
            name='shared_with',
            field=models.ForeignKey(related_name=b'shared_by', to='backend1.UserProfile'),
        ),
    ]
