# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0003_auto_20141020_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCreatedCreature',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('eye', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
