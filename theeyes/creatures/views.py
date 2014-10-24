from rest_framework import viewsets
from rest_framework import mixins

from .serializers import (
    CreatureSerializer,
    HeroAnimationSerializer,
    UserCreatedCreatureSerializer,
    InteractionSerializer,
)

from .models import (
    Creature,
    HeroAnimation,
    UserCreatedCreature,
    Interaction,
)


class CreatureSet(viewsets.ReadOnlyModelViewSet):
    queryset = Creature.objects.all()
    serializer_class = CreatureSerializer


class HeroAnimationSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeroAnimation.objects.all()
    serializer_class = HeroAnimationSerializer


class UserCreatedCreatureSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    queryset = UserCreatedCreature.objects.all()
    serializer_class = UserCreatedCreatureSerializer


class InteractionSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer
