# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='pastebin_log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('syntax', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('visitors', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
