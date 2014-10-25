# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0007_auto_20141024_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='creaturequestion',
            name='enabled',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
