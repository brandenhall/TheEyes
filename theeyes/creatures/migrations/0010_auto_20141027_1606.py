# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0009_creature_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='creature',
            name='overlay',
            field=models.FileField(blank=True, null=True, upload_to='', help_text='Any overay for the eye (JSON)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creature',
            name='pupil_mask',
            field=models.FileField(blank=True, null=True, upload_to='', help_text='Mask showing valid pupil positions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='creaturequestionresponse',
            name='loops',
            field=models.PositiveIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='heroanimation',
            name='loops',
            field=models.PositiveIntegerField(default=1),
            preserve_default=True,
        ),
    ]
