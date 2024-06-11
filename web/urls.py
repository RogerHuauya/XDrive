from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path("master_files/", views.masterFileListView, name="master_files"),
]
