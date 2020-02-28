from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('escalate', views.escalate, name="escalate"),
    path('sendorderemail', views.sendorderemail, name="escalate")

]