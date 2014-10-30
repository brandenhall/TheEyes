# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0010_auto_20141027_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='creature',
            name='is_overlay',
            field=models.BooleanField(default=True, verbose_name='Layer is an overlay'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='creature',
            name='overlay',
            field=models.FileField(blank=True, verbose_name='Layer', null=True, upload_to='', help_text='Extra layer for the eye (JSON)'),
        ),
    ]
