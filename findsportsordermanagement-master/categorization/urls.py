from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categorization_file_upload', views.categorization_file_upload, name='categorization_file_upload'),
    path('downloadfilewithcomments', views.downloadfilewithcomments, name='downloadfilewithcomments'),

]
