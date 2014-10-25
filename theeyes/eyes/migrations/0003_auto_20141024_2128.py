# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eyes', '0002_auto_20141020_2233'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eye',
            options={'ordering': ['number']},
        ),
    ]
