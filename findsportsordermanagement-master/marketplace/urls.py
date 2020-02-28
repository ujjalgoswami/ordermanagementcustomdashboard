from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('uploadcsv',views.file_upload, name='uploadcsv'),
    path('viewjson',views.viewjson, name='viewjson'),
    path('viewjsonerrors',views.viewjsonerrors, name='viewjsonerrors'),
    path('simple_upload',views.simple_upload, name='simple_upload'),



]