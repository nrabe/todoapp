# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0010_auto_20140910_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='todolist',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'active'), (1, b'archived')]),
            preserve_default=False,
        ),
    ]
