from django.urls import path

# from upload.views import MasterFileListView
from . import views

urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("upload_file_chunk",
         views.upload_file_chunk,
         name="upload_file_chunk"),
    path("master_files/", views.masterFileListView, name="master_files"),

]
