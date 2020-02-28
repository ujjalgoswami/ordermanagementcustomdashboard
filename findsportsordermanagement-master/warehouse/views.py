from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime
# Create your views here.
from purchaseorder.views import viewallpurchaseorders, viewPendingSubmitCreatedPurchaseOrders, \
    viewalluncheckedpurchaseorders, viewpurchaseorder, get_purchase_order_id_details
from purchaseorder.models import purchaseorder, orderline

@login_required
def index(request):

    # Displaying unique dates
    supplier_name = request.GET.get('supplier_name')
    if not (supplier_name is None):
        # Date filter passed , show all purchase ids on that date

        return viewallpurchaseorders(request, date_created=None, template=None, supplier_name=supplier_name)


    else:
        # No date filter is passed . Show all available created on dates

        list_of_unique_dates = viewallpurchaseorders(request)
        list_of_submit_pending = viewPendingSubmitCreatedPurchaseOrders()
        dict_purchase_order_submitted_date = viewalluncheckedpurchaseorders(isWarehouse=True)

        purchaseordersuppliers = purchaseorder.objects.filter(received=False, submitted=True).order_by().values(
            'supplier_name').distinct()
        list_of_suppliername_dicts = list(purchaseordersuppliers)
        list_of_supplier_names = [d['supplier_name'] for d in list_of_suppliername_dicts]
        # print(list_of_supplier_names)

        return render(request, 'warehouse/purchaseorders.html',
                      {"warehouse": True, "unique_dates": True, "list_of_submit_pending": list_of_submit_pending,
                       "list_of_unique_dates": sorted(list_of_unique_dates, reverse=True),
                       "dict_purchase_order_submitted_date": dict_purchase_order_submitted_date,
                       "list_of_supplier_names": list_of_supplier_names})
