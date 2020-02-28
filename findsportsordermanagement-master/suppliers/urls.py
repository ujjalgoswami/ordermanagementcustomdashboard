from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('suppliers', views.index, name='suppliers'),
    path('updatesupplierdetails', views.updatesupplierdetails, name='updatesupplierdetails'),
path('viewoutofstockpercentage', views.viewoutofstockpercentage, name='viewoutofstockpercentage'),



]
