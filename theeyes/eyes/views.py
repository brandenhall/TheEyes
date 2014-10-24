from rest_framework import viewsets
from .serializers import EyeSerializer
from .models import Eye


class EyeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Eye.objects.all()
    serializer_class = EyeSerializer
