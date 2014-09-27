# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0009_auto_20140910_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todolistitem',
            name='created_by',
            field=models.ForeignKey(related_name=b'+', to=settings.AUTH_USER_MODEL),
        ),
    ]
