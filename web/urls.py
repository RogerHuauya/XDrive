from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('upload_file_chunk', views.upload_file_chunk,
         name='upload_file_chunk'),
]
