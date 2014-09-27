# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0012_auto_20140910_1632'),
    ]

    operations = [
        migrations.RenameField(
            model_name='todolistitem',
            old_name='todo',
            new_name='text',
        ),
        migrations.AddField(
            model_name='todolistitem',
            name='todolist',
            field=models.ForeignKey(default=1, to='backend1.TODOList'),
            preserve_default=False,
        ),
    ]
