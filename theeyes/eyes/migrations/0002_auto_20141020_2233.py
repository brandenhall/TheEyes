# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eyes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eyerelationship',
            name='eye',
            field=models.ForeignKey(to='eyes.Eye', related_name='preferences'),
        ),
        migrations.AlterField(
            model_name='eyerelationship',
            name='relative',
            field=models.ForeignKey(to='eyes.Eye', related_name='relatives'),
        ),
    ]
