from .models import ChunkedFile, MasterFile
from rest_framework import viewsets
from .serializers import ChunkedFileSerializer, MasterFileSerializer
from django.utils import timezone
from django.views.generic import ListView

class MasterFileListView(ListView):
    model = MasterFile
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context
    
class MasterFileModelViewSet(viewsets.ModelViewSet):
    queryset = MasterFile.objects.all()
    serializer_class = MasterFileSerializer


class ChunkedFileModelViewSet(viewsets.ModelViewSet):
    queryset = ChunkedFile.objects.all()
    serializer_class = ChunkedFileSerializer
