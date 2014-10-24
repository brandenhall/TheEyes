# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('creatures', '0002_creaturequestionresponse_result'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroAnimation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, help_text='Name of this animation')),
                ('animation', models.FileField(upload_to='', help_text='Animation (JSON)')),
                ('weight', models.FloatField(default=1.0, help_text='Weight for this animation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='creatureheroanimation',
            name='creature',
        ),
        migrations.DeleteModel(
            name='CreatureHeroAnimation',
        ),
    ]
