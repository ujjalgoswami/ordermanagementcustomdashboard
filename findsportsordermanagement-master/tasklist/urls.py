from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('newtask', views.newtask, name="newtask"),
    path('newgroup', views.newgroup, name="newgroup"),
    path('updatetask', views.updatetask, name="updatetask"),
    path('recurring_task_completed', views.recurring_task_completed, name="recurring_task_completed"),

]
