# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0003_auto_20140731_1841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='lon',
        ),
        migrations.AlterField(
            model_name='mood',
            name='lat',
            field=models.DecimalField(max_digits=8, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='mood',
            name='lon',
            field=models.DecimalField(max_digits=8, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.DecimalField(max_digits=8, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='lon',
            field=models.DecimalField(max_digits=8, decimal_places=5, blank=True),
        ),
    ]
