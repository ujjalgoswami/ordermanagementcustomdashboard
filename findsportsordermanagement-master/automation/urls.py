from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('undispatchedorders', views.undispatchedorders, name='undispatchedorders'),
    path('dispatchedorders', views.dispatchedorders, name='dispatchedorders'),
    path('setdispathedorders', views.setdispathedorders, name='dispatchedorders'),
    path('setpurchaseorders', views.setpurchaseorders, name='setpurchaseorders'),
    path('getnotifications', views.getnotifications, name='getnotifications'),
    path('stock_update_supplier_details', views.stock_update_supplier_details, name='stock_update_supplier_details'),


]
