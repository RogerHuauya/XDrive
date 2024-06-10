from django.shortcuts import render, get_object_or_404
import os
from django.http import JsonResponse, HttpResponse, Http404
from upload.models import MasterFile, ChunkedFile
from django.views.decorators.csrf import csrf_exempt


def home_page(request):
    context = {
        "variable": "value",
    }
    return render(request, "web/index.html", context)


def masterFileListView(request):
    master_files = MasterFile.objects.all()
    # file = models.FileField(upload_to='master_files/', null=True, blank=True)
    # file_name = models.CharField(max_length=255)
    # md5_checksum = models.CharField(max_length=32)
    # number_of_chunks = models.PositiveIntegerField()
    # uploaded_at = models.DateTimeField(auto_now_add=True)
    return render(
        request, "upload/masterfile_list.html", {"master_files": master_files}
    )


@csrf_exempt
def upload_file_chunk(request):
    if request.method == "POST":
        try:
            chunk = request.FILES.get("file")
            file_name = request.POST.get("file_name")
            chunk_number = int(request.POST.get("chunk_number"))
            total_chunks = int(request.POST.get("total_chunks"))
            file_id = request.POST.get("file_id")

            if file_id:
                master_file = MasterFile.objects.get(id=file_id)
            else:
                master_file = MasterFile.objects.create(
                    file_name=file_name, number_of_chunks=total_chunks
                )

            chunked_file = ChunkedFile.objects.create(
                master_file=master_file, file=chunk, chunk_number=chunk_number
            )

            print(
                f"Chunks subidos para {master_file.id}:"
                f" {master_file.chunkedfile_set.count()} de {total_chunks}"
            )
            print(f"Ruta del archivo chunk: {chunked_file.file.path}")

            if master_file.is_complete():
                file_path = os.path.join("media/master_files",
                                         master_file.file_name)
                with open(file_path, "wb") as complete_file:
                    for i in range(total_chunks):
                        chunk = ChunkedFile.objects.get(
                            master_file=master_file, chunk_number=i
                        )
                        with open(chunk.file.path, "rb") as chunk_file:
                            complete_file.write(chunk_file.read())
                        os.remove(chunk.file.path)
                master_file.file = file_path
                master_file.save()

                return JsonResponse({
                    "file_id": master_file.id,
                    "is_complete": True
                    })

            return JsonResponse({
                "file_id": master_file.id,
                "is_complete": False
                })

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)


def file_list(request):
    files = MasterFile.objects.all()
    return render(request, "fileapp/file_list.html", {"files": files})


def download_file(request, file_id):
    try:
        master_file = MasterFile.objects.get(id=file_id)
        if not master_file.is_complete():
            return HttpResponse(status=400,
                                content="File upload is not complete.")
        response = HttpResponse(
            master_file.file, content_type="application/octet-stream"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{master_file.file_name}"'
        )
        return response
    except MasterFile.DoesNotExist:
        raise Http404


def view_file(request, file_id):
    master_file = get_object_or_404(MasterFile, id=file_id)
    if not master_file.file:
        raise Http404("File not found")

    file_path = master_file.file.path
    with open(file_path, "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")
