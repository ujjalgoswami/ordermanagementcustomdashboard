from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generatePurchaseOrder', views.generatePurchaseOrder, name='generatepurchaseorder'),
    path('changepurchaseorderstatus', views.changepurchaseorderstatus, name='changepurchaseorderstatus'),
    path('processcronnewbackorder', views.processcronnewbackorder, name='processcronnewbackorder'),
    path('purchaseorderstockconfirm', views.purchaseorderstockconfirm, name='purchaseorderstockconfirm'),
    path('subpurchaseorders', views.subpurchaseorders, name='subpurchaseorders'),

]
