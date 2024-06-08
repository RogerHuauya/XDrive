from .models import ChunkedFile, MasterFile
from rest_framework import viewsets
from .serializers import ChunkedFileSerializer, MasterFileSerializer


class MasterFileModelViewSet(viewsets.ModelViewSet):
    queryset = MasterFile.objects.all()
    serializer_class = MasterFileSerializer


class ChunkedFileModelViewSet(viewsets.ModelViewSet):
    queryset = ChunkedFile.objects.all()
    serializer_class = ChunkedFileSerializer
