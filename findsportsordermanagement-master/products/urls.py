from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:sku>', views.index, name='get_product_details')
]