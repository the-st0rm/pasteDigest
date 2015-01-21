# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='paste_posts',
            field=models.ManyToManyField(to='main.pastebin_log'),
            preserve_default=True,
        ),
    ]
