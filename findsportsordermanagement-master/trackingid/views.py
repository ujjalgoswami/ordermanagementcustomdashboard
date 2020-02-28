from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date
# Create your views here.
from purchaseorder.views import viewallpurchaseorders
import datetime
import numpy as np
from purchaseorder.models import purchaseorder, orderid_purchaseorderid


@login_required
def index(request):
    # Displaying unique dates
    created_on = request.GET.get('created_on')
    if not (created_on is None):
        # Date filter passed , show all purchase ids on that date

        date_time_obj = datetime.datetime.strptime(created_on, '%b. %d, %Y')
        return viewallpurchaseorders(request, date_time_obj, "trackingid.html")

    else:
        # No date filter is passed . Show all available created on dates


        #print(List_of_tracking_pending,error_count_delayed_tracking)

        List_of_tracking_pending=trackingpending()


        list_of_unique_dates = viewallpurchaseorders(request)

        return render(request, 'trackingid.html',
                      {"trackingid": True, "unique_dates": True,
                       "list_of_unique_dates": sorted(list_of_unique_dates, reverse=True),"List_of_tracking_pending":List_of_tracking_pending})

def trackingpending():
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)


    dict_purchaseorder_submitted = {}
    try:
        p_order = purchaseorder.objects.filter(submitted_date__isnull=False, legacy_purchase_id=False, tracking_id="NA",received=False)

        for temp in p_order:
            if (temp.submitted_date == "" or temp.submitted_date == None):
                dict_purchaseorder_submitted[temp.purchase_orderid] = (
                temp.purchase_orderid, 0, temp.submitted_date, temp.alias,temp.internal_notes)
            else:
                business_days = np.busday_count(temp.submitted_date, today_date)
                dict_purchaseorder_submitted[temp.purchase_orderid] = (
                    temp.purchase_orderid, str(business_days), temp.submitted_date, temp.alias,temp.internal_notes)
    except:
        print("Something went wrong!")

    list_of_purchase_orders=list(dict_purchaseorder_submitted.keys())
    dict_pid_affected_orders={}
    for purchase_order in list_of_purchase_orders:

        orderid_purchaseorderid_objects=orderid_purchaseorderid.objects.filter(purchase_orderid=purchase_order)
        list_of_affected_orderids = [result.order_id for result in
                                     orderid_purchaseorderid_objects]
        dict_pid_affected_orders[purchase_order]=len(set(list_of_affected_orderids))

    error_count_delayed_tracking = 0
    List_of_tracking_pending = [(order, days, date, alias,dict_pid_affected_orders[order],notes) for order, days, date, alias,notes in
                                dict_purchaseorder_submitted.values()]
    list1 = list(map(list, zip(*List_of_tracking_pending)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            if not (list1[1][index] == 0):
                list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 3):
                error_count_delayed_tracking += 1

        List_of_tracking_pending = zip(list1[0], list1[1], list1[2], list1[3], list1[4],list1[5])
        List_of_tracking_pending = list(List_of_tracking_pending)
    List_of_tracking_pending = sorted(List_of_tracking_pending, key=lambda x: x[1],
                                      reverse=True)
    return List_of_tracking_pending

def trackingid(request):
    dict_sku_orderid = {}

    if request.method == 'POST':

        temp_dict = {}

        dict_of_post_items = request.POST.items()
        list_of_purchaseorders = []
        list_of_trackingids = []
        list_of_couriers = []
        created_on_date = ""

        for index, item in enumerate(dict_of_post_items):
            tupple = item
            key = tupple[0]
            value = tupple[1]
            if not ("csrfmiddlewaretoken" == key):
                if ("created_on_date" == key):
                    created_on_date = value
                elif ("purchaseorderid" in key):
                    list_of_purchaseorders.append(value)
                elif ("trackingid" in key):
                    list_of_trackingids.append(value)
                elif ("courier" in key):
                    list_of_couriers.append(value)

        for index2 in range(0, len(list_of_purchaseorders)):
            temp_list = []
            for temp in request.POST.items():
                key1 = temp[0]
                val1 = temp[1]
                if (list_of_purchaseorders[index2] in key1):
                    temp_list.append(val1)

            temp_dict[list_of_purchaseorders[index2]] = temp_list

        for pid in temp_dict:
            purchase_order_id = pid
            tracking_id = temp_dict[pid][1]
            courier = temp_dict[pid][2]
            p_order = purchaseorder.objects.get(alias=str(purchase_order_id))
            p_order.tracking_id = tracking_id
            p_order.courier = courier
            p_order.save(update_fields=['tracking_id'])
            p_order.save(update_fields=['courier'])

        return redirect('/trackingid/?created_on=' + str(created_on_date))
