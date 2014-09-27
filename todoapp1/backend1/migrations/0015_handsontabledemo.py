# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('backend1', '0014_auto_20140920_2238'),
    ]

    operations = [
        migrations.CreateModel(
            name='HandsontableDemo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rname', models.CharField(default=b'(no rname)', help_text=b'Internal object name (fit for admin/backend tasks only)', max_length=255)),
                ('date_created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('date_updated', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('test_charfield', models.CharField(max_length=255)),
                ('test_int_choices_null', models.IntegerField(null=True, choices=[(0, b'zero'), (1, b'one'), (2, b'two')])),
                ('test_int_choices', models.IntegerField(default=0, choices=[(0, b'zero'), (1, b'one'), (2, b'two')])),
                ('test_integer', models.IntegerField()),
                ('test_integer_null', models.IntegerField(null=True)),
                ('test_decimal', models.DecimalField(max_digits=7, decimal_places=2)),
                ('test_decimal_null', models.DecimalField(null=True, max_digits=7, decimal_places=2)),
                ('test_boolean', models.BooleanField(default=False)),
                ('test_boolean_null', models.NullBooleanField()),
                ('test_datetime_null', models.DateTimeField(null=True)),
                ('test_date', models.DateField(null=True)),
                ('test_time', models.TimeField(null=True)),
                ('test_foreign_key', models.ForeignKey(related_name=b'+', to='backend1.UserProfile')),
                ('test_foreign_key_null', models.ForeignKey(related_name=b'+', to='backend1.UserProfile', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
