# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0006_auto_20141022_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='creature',
            name='maximum_blink',
            field=models.IntegerField(help_text='Maximum frames between blinks @ 30fps', default=150),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creature',
            name='minimum_blink',
            field=models.IntegerField(help_text='Minimum frames between blinks @ 30fps', default=60),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='creature',
            name='circadian_offset',
            field=models.FloatField(help_text='Offset from equal wake-to-sleep', default=0),
        ),
    ]
