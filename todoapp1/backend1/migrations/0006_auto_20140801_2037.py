# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0005_auto_20140731_2004'),
        (b'auth', b'__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='mood',
            name='user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='mood',
            name='profile',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
