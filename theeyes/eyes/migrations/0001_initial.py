# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Eye',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('number', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EyeRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('position', models.PositiveSmallIntegerField(verbose_name='Position', default=0)),
                ('eye', models.ForeignKey(related_name='owner_eye', to='eyes.Eye')),
                ('relative', models.ForeignKey(related_name='relative_eye', to='eyes.Eye')),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
    ]
