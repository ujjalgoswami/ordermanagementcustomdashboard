from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('setstockupdatestats', views.setstockupdatestats, name='setstockupdatestats'),
    path('bulkdownload', views.bulkdownload, name='setstockupdatestats'),
    path('pending_stock_update_suppliers_for_today', views.pending_stock_update_suppliers_for_today, name='pending_stock_update_suppliers_for_today'),
]
