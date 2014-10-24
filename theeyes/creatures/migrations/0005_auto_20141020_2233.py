# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0004_usercreatedcreature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creaturequestion',
            name='creature',
            field=models.ForeignKey(to='creatures.Creature', related_name='questions'),
        ),
        migrations.AlterField(
            model_name='creaturequestionresponse',
            name='question',
            field=models.ForeignKey(to='creatures.CreatureQuestion', related_name='responses'),
        ),
    ]
