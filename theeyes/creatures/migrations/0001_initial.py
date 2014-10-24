# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Creature',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of this creature', max_length=255)),
                ('eye', models.FileField(help_text='Static image of the eye (JSON)', upload_to='')),
                ('circadian_offset', models.FloatField(help_text='Start of wake/sleep cycle (minutes)', default=0)),
                ('circadian_period', models.FloatField(help_text='Period of wake/sleep cycle (minutes)', default=20)),
                ('restlessness', models.FloatField(help_text='How regularly creature will change eyes (percent)', default=0.05)),
                ('maximum_speed', models.FloatField(help_text='Maximum speed of the creature (percent)', default=1.0)),
                ('minimum_speed', models.FloatField(help_text='Minimum speed of the creature (percent)', default=0.0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreatureHeroAnimation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('animation', models.FileField(help_text='Animation (JSON)', upload_to='')),
                ('weight', models.FloatField(help_text='Weight for this animation', default=1.0)),
                ('creature', models.ForeignKey(to='creatures.Creature')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreatureQuestion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('question', models.TextField(help_text='Question the creature is asking')),
                ('creature', models.ForeignKey(to='creatures.Creature')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreatureQuestionResponse',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('response', models.CharField(help_text='Reponse', max_length=100)),
                ('animation', models.FileField(help_text='Animation (JSON)', upload_to='')),
                ('question', models.ForeignKey(to='creatures.CreatureQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('response', models.ForeignKey(to='creatures.CreatureQuestionResponse')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
