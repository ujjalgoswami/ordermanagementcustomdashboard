from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('newticket', views.newticket, name="newticket"),
    path('updateticket', views.updateticket, name="updateticket")


]