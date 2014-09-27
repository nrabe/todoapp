# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0004_auto_20140731_1848'),
    ]

    operations = [
        migrations.RenameField(
            model_name='place',
            old_name='cached_mood_count',
            new_name='cached_moods_count',
        ),
    ]
