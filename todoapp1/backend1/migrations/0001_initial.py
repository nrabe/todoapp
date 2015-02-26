# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import todoapp1.backend1.models
import django_extensions.db.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HandsontableDemo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rname', models.CharField(default=todoapp1.backend1.models._unique_rname, help_text=b'Internal object name (fit for admin/backend tasks, must be unique)', unique=True, max_length=255, blank=True)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('date_updated', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('test_charfield', models.CharField(max_length=255)),
                ('test_int_choices_null', models.IntegerField(blank=True, null=True, choices=[(0, b'zero'), (1, b'one'), (2, b'two')])),
                ('test_int_choices', models.IntegerField(default=0, choices=[(0, b'zero'), (1, b'one'), (2, b'two')])),
                ('test_integer', models.IntegerField()),
                ('test_integer_null', models.IntegerField(null=True, blank=True)),
                ('test_decimal', models.DecimalField(max_digits=7, decimal_places=2)),
                ('test_decimal_null', models.DecimalField(null=True, max_digits=7, decimal_places=2, blank=True)),
                ('test_boolean', models.BooleanField(default=False)),
                ('test_boolean_null', models.NullBooleanField()),
                ('test_datetime_null', models.DateTimeField(null=True, blank=True)),
                ('test_date', models.DateField(null=True, blank=True)),
                ('test_time', models.TimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TODOList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rname', models.CharField(default=todoapp1.backend1.models._unique_rname, help_text=b'Internal object name (fit for admin/backend tasks, must be unique)', unique=True, max_length=255, blank=True)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('date_updated', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('comments', models.TextField(blank=True)),
                ('category', models.CharField(max_length=255, blank=True)),
                ('status', models.IntegerField(default=0, choices=[(0, b'active'), (1, b'archived')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TODOListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rname', models.CharField(default=todoapp1.backend1.models._unique_rname, help_text=b'Internal object name (fit for admin/backend tasks, must be unique)', unique=True, max_length=255, blank=True)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('date_updated', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('text', models.CharField(max_length=255)),
                ('status', models.IntegerField(default=0, choices=[(0, b'not started'), (1, b'started'), (2, b'completed')])),
                ('todolist', models.ForeignKey(related_name=b'todolistitems', to='backend1.TODOList')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TODOListSharing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rname', models.CharField(default=todoapp1.backend1.models._unique_rname, help_text=b'Internal object name (fit for admin/backend tasks, must be unique)', unique=True, max_length=255, blank=True)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('date_updated', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('todolist', models.ForeignKey(to='backend1.TODOList')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
            model_name='handsontabledemo',
            name='test_foreign_key_null',
            field=models.ForeignKey(related_name=b'+', blank=True, to='backend1.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='handsontabledemo',
            name='test_foreign_key',
            field=models.ForeignKey(related_name=b'+', to='backend1.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolist',
            name='created_by',
            field=models.ForeignKey(to='backend1.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='last_updated_by',
            field=models.ForeignKey(related_name=b'+', to='backend1.UserProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='created_by',
            field=models.ForeignKey(related_name=b'+', to='backend1.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistsharing',
            name='shared_with',
            field=models.ForeignKey(related_name=b'shared_by', to='backend1.UserProfile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='todolistsharing',
            name='shared_by',
            field=models.ForeignKey(related_name=b'shared_with', to='backend1.UserProfile'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='todolistsharing',
            unique_together=set([('todolist', 'shared_with')]),
        ),
    ]
