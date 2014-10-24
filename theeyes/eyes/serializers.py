from rest_framework import serializers
from .models import Eye


class EyeRelationshipField(serializers.RelatedField):
    def to_native(self, value):
        return value.relative.number


class EyeSerializer(serializers.ModelSerializer):
    preferences = EyeRelationshipField(many=True)

    class Meta:
        model = Eye
        fields = ('number', 'preferences',)
