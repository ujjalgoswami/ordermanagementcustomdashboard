from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userlogin', views.userlogin, name='userlogin'),
    path('logout', views.logout, name='userlogin'),
]