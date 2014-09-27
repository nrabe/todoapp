# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0011_todolist_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todolist',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'active'), (1, b'archived')]),
        ),
        migrations.AlterField(
            model_name='todolistitem',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, b'not started'), (1, b'started'), (2, b'completed')]),
        ),
    ]
