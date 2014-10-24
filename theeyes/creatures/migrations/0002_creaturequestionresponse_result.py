# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creaturequestionresponse',
            name='result',
            field=models.IntegerField(default=0, choices=[(0, 'More awake'), (1, 'Less awake'), (2, 'More enagaged'), (3, 'Less engaged')]),
            preserve_default=True,
        ),
    ]
