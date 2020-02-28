from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
handler404 = 'zendesk.views.my_custom_page_not_found_view'
