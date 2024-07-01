import io
from .models import ChunkedFile, MasterFile
from rest_framework import viewsets
from .serializers import ChunkedFileSerializer, MasterFileSerializer
from django.utils import timezone
from django.views.generic import ListView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.files.base import ContentFile


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

    @action(detail=False, methods=['get'], url_path='last-chunk')
    def last_chunk(self, request):
        master_file_id = request.query_params.get('master_file_id')
        if not master_file_id:
            return Response({"error": "master_file_id parameter is required"},
                            status=400)

        master_file = get_object_or_404(MasterFile, id=master_file_id)
        last_chunk = ChunkedFile.objects.filter(master_file=master_file).\
            order_by('-chunk_number').first()

        if not last_chunk:
            return Response({"message": "No chunks found for this "
                                        "master file"}, status=404)

        serializer = self.get_serializer(last_chunk)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='merge-chunks')
    def merge_chunks(self, request):
        master_file_id = request.query_params.get('master_file_id')
        if not master_file_id:
            return Response({"error": "master_file_id parameter is required"},
                            status=400)

        master_file = get_object_or_404(MasterFile, id=master_file_id)
        chunks = ChunkedFile.objects.filter(master_file=master_file)\
            .order_by('chunk_number')

        if not chunks.exists():
            return Response({"error": "No chunks available for "
                                      "this master file"}, status=404)

        combined_file_content = io.BytesIO()
        for chunk in chunks:
            with chunk.file.open('rb') as f:
                combined_file_content.write(f.read())

        combined_file_content.seek(0)
        django_file = ContentFile(combined_file_content.read(),
                                  name=master_file.file_name)
        combined_file_content.close()
        master_file.file.save(master_file.file_name, django_file)

        response = HttpResponse(django_file,
                                content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; ' \
                                          f'filename="{master_file.file_name}"'
        print(response['Content-Disposition'])
        return response

    @action(detail=False, methods=['get'], url_path='download')
    def download_file(self, request):
        master_file_id = request.query_params.get('master_file_id')
        if not master_file_id:
            return Response({"error": "master_file_id parameter is required"},
                            status=400)

        master_file = get_object_or_404(MasterFile,
                                        id=master_file_id)

        if not master_file.file:
            return Response({"error": "File not found for this master_file"},
                            status=404)

        with master_file.file.open('rb') as f:
            response = HttpResponse(f.read(),
                                    content_type='application/octet-stream')
            response['Content-Disposition'] = (
                f'attachment; filename="{master_file.file_name}"'
            )

        return response
