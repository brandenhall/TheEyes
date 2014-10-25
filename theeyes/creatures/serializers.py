import json
import logging

from django.conf import settings
from rest_framework import serializers
from .models import (
    Creature,
    CreatureQuestion,
    CreatureQuestionResponse,
    HeroAnimation,
    UserCreatedCreature,
    Interaction,
)


class JSONFileField(serializers.Field):
    def to_native(self, value):
        with open(settings.MEDIA_ROOT + value.name) as data_file:
            return json.load(data_file)


class JSONField(serializers.WritableField):
    def to_native(self, value):
        try:
            return json.loads(value)
        except ValueError:
            return []

    def from_native(self, data):
        try:
            return json.dumps(data)
        except ValueError:
            return "[]"


class CreatureQuestionResponseSerializer(serializers.ModelSerializer):
    animation = JSONFileField()
    class Meta:
        model = CreatureQuestionResponse
        fields = ('id', 'response', 'animation', 'result')


class CreatureQuestionSerializer(serializers.ModelSerializer):
    responses = CreatureQuestionResponseSerializer(many=True)

    class Meta:
        model = CreatureQuestion
        fields = ('question', 'responses', 'enabled')


class CreatureSerializer(serializers.ModelSerializer):
    eye = JSONFileField()
    questions = CreatureQuestionSerializer(many=True)

    class Meta:
        model = Creature
        fields = (
            'name',
            'eye',
            'circadian_offset',
            'circadian_period',
            'sclera_color',
            'lid_color',
            'restlessness',
            'minimum_speed',
            'maximum_speed',
            'minimum_blink',
            'maximum_blink',
            'questions'
        )


class HeroAnimationSerializer(serializers.ModelSerializer):
    animation = JSONFileField()

    class Meta:
        model = HeroAnimation
        fields = ('name', 'animation', 'weight')


class InteractionSerializer(serializers.ModelSerializer):
    animation = JSONFileField()

    class Meta:
        model = Interaction
        fields = ('timestamp', 'response',)


class UserCreatedCreatureSerializer(serializers.ModelSerializer):
    eye = JSONField()

    class Meta:
        model = UserCreatedCreature
        fields = ('timestamp', 'eye')

