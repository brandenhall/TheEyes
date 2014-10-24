# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0005_auto_20141020_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='creature',
            name='lid_color',
            field=models.CharField(default='000000', help_text="Color of the creature's eyelid", max_length=6),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creature',
            name='sclera_color',
            field=models.CharField(default='ffffff', help_text="Color of the creature's scelere", max_length=6),
            preserve_default=True,
        ),
    ]
