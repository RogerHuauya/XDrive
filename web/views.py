from django.shortcuts import render
from upload.models import MasterFile


def home_page(request):
    return render(request, 'web/index.html')


def masterFileListView(request):
    master_files = MasterFile.objects.all()
    return render(
        request, "upload/masterfile_list.html", {"master_files": master_files}
    )
