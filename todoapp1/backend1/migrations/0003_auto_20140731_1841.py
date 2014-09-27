# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0002_auto_20140731_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='cached_mood_count',
            field=models.CharField(default=b'', max_length=16384, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_uid',
            field=models.CharField(default=b'dummy', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mood',
            name='lat',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='mood',
            name='lon',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='mood',
            name='moodtype',
            field=models.ForeignKey(to='backend1.MoodType'),
        ),
        migrations.AlterField(
            model_name='mood',
            name='place',
            field=models.ForeignKey(to='backend1.Place', null=True),
        ),
        migrations.AlterField(
            model_name='mood',
            name='profile',
            field=models.ForeignKey(to='backend1.Profile'),
        ),
        migrations.AlterField(
            model_name='moodtype',
            name='moodtype',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='lon',
            field=models.FloatField(blank=True),
        ),
    ]
