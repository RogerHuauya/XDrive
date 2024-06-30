from django.shortcuts import render
from upload.models import MasterFile


def home_page(request):
    return render(request, 'index.html')


def masterFileListView(request):
    master_files = MasterFile.objects.all()
    return render(
        request, "components/list.html", {"master_files": master_files}
    )
