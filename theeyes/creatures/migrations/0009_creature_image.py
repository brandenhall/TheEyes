# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0008_creaturequestion_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='creature',
            name='image',
            field=models.ImageField(upload_to='', null=True, help_text='Image of the eye', blank=True, default=None),
            preserve_default=True,
        ),
    ]
