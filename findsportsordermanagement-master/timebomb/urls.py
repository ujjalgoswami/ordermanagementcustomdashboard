from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test-import.csv', views.getfile, name='index'),
    path('timebomb_file_upload', views.timebomb_file_upload, name='index')
]