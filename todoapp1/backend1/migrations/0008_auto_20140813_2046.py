# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0007_auto_20140808_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='google_place_data',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='place',
            name='google_place_id',
            field=models.CharField(max_length=255, unique=True, null=True),
            preserve_default=True,
        ),
    ]
