from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import json
import requests
from datetime import date
import numpy as np
import datetime
import findsportsordermanagement.settings as settings
from django.db import connection

# Create your views here.
from netoapihook.models import OrderHistory
from suppliers.models import Supplier_Details, SupplierNew
from django.contrib import messages
from datetime import date, timedelta
from purchaseorder.models import purchaseorder, orderline
from django.db.models import F

import pandas as pd

from os import listdir
from os.path import isfile, join

from stockupdate.views import getfile


def updatesupplierdetails(request):
    if request.method == 'POST':


        dict_of_post_items = request.POST.items()
        for temp in dict_of_post_items:
            key, value = temp
            if ("download_stock_update" in key):
                stock_update_file_name = request.POST.get('stock_update_file_name')
                return getfile(stock_update_file_name)

        supplier_name = request.POST.get('supplier_name')

        contact_name = request.POST.get('contact_name')
        contact_email = request.POST.get('contact_email')
        contact_number = request.POST.get('contact_number')
        contact_position = request.POST.get('contact_position')

        supplier_details = Supplier_Details.objects.get(supplier_name=supplier_name)

        supplier_details.contact_name = contact_name
        supplier_details.contact_email = contact_email
        supplier_details.contact_number = contact_number
        supplier_details.contact_position = contact_position
        supplier_details.save(update_fields=['contact_name'])
        supplier_details.save(update_fields=['contact_email'])
        supplier_details.save(update_fields=['contact_number'])
        supplier_details.save(update_fields=['contact_position'])

        messages.info(request, "Supplier Details Updated!")

        return redirect('/suppliers/?supplier_name=' + supplier_name)


def viewoutofstockpercentage(request):
    days_before = (date.today() - timedelta(days=10)).isoformat()

    with connection.cursor() as cursor:
        cursor.execute(
            "select sn.primarysupplier,count(sn.primarysupplier) from public.purchaseorder_orderline ol,public.purchaseorder_purchaseorder po,public.suppliers_suppliernew sn where po.purchase_orderid=ol.purchase_orderid_id and po.submitted_date>%s and  ol.instock<ol.qty   and ol.order_line_id=sn.order_line_id group by sn.primarysupplier  ",
            [days_before])
        row = cursor.fetchall()

    dict_of_supplier_not_in_stock = dict(row)
    # try:
    #     dict_of_supplier_not_in_stock['PhoenixLeisureGroup'] = int(
    #         dict_of_supplier_not_in_stock['PhoenixLeisureGroup']) + int(
    #         dict_of_supplier_not_in_stock['PhoenixLeisureGroup_2'])
    # except:
    #     dict_of_supplier_not_in_stock['PhoenixLeisureGroup'] = int(
    #         dict_of_supplier_not_in_stock['PhoenixLeisureGroup_2'])

    # try:
    #     del dict_of_supplier_not_in_stock['PhoenixLeisureGroup_2']
    # except KeyError:
    #     pass

    with connection.cursor() as cursor:
        cursor.execute(
            "select sn.primarysupplier,count(sn.primarysupplier) from public.purchaseorder_orderline ol,public.purchaseorder_purchaseorder po,public.suppliers_suppliernew sn where po.purchase_orderid=ol.purchase_orderid_id and po.submitted_date>%s   and ol.order_line_id=sn.order_line_id group by sn.primarysupplier  ",
            [days_before])
        row = cursor.fetchall()

    dict_of_supplier_total = dict(row)

    # try:
    #     dict_of_supplier_total['PhoenixLeisureGroup'] = int(dict_of_supplier_total['PhoenixLeisureGroup']) + int(
    #         dict_of_supplier_total['PhoenixLeisureGroup_2'])
    # except:
    #     print(dict_of_supplier_total)
    #
    # try:
    #     del dict_of_supplier_total['PhoenixLeisureGroup_2']
    # except KeyError:
    #     pass

    list_of_out_of_stock = []
    list_of_out_of_percentage = []
    list_of_categories = []
    list_of_total_orders = []
    for supplier in dict_of_supplier_not_in_stock:
        temp_dict3 = {}
        temp_dict3['value'] = dict_of_supplier_total[supplier]
        list_of_total_orders.append(temp_dict3)

        temp_dict2 = {}
        temp_dict2['label'] = supplier
        list_of_categories.append(temp_dict2)

        temp_dict = {}
        temp_dict['value'] = (dict_of_supplier_not_in_stock[supplier])
        list_of_out_of_stock.append(temp_dict)

        temp_dict4 = {}
        temp_dict4['value'] = (int(dict_of_supplier_not_in_stock[supplier]) / int(
            dict_of_supplier_total[supplier])) * 100
        list_of_out_of_percentage.append(temp_dict4)

    data = {
        "type": "overlappedColumn2d",
        "renderAt": "chart-container",
        "width": "900",
        "height": "700",
        "dataFormat": "json",
        "dataSource": {
            "chart": {
                "caption": "Supplier out of stock performance (10 Days)",
                "subCaption": "Based on submitted and received purchase orders",
                "xAxisName": "Suppliers",
                "yAxisName": "Orders",
                "showValues": "0",
                "theme": "fusion",
                "exportEnabled": "1",
                "exportMode": "client"
            },
            "categories": [{
                "category": list_of_categories
            }],
            "dataset": [{
                "seriesname": "Total orders",
                "data": list_of_total_orders
            }, {
                "seriesname": "Out of stock",
                "data": list_of_out_of_stock
            },
                {
                    "seriesname": "Percentage",
                    "data": list_of_out_of_percentage
                }
            ]
        }
    }
    return JsonResponse(data)

@login_required
def index(request):
    if request.method == 'POST':
        temp_dict = {}

        dict_of_post_items = request.POST.items()

        list_of_supplier_name = []
        list_of_status = []
        for index, item in enumerate(dict_of_post_items):
            tupple = item
            key = tupple[0]
            value = tupple[1]
            if not ("csrfmiddlewaretoken" == key):
                if ("status" in key):
                    list_of_supplier_name.append(key.split(":")[0])
                    list_of_status.append(value)

        supplier_name = list_of_supplier_name[0]
        supplier_status = list_of_status[0]

        supplier_details = Supplier_Details.objects.get(
            supplier_name=supplier_name)

        if (supplier_status == 'Active'):
            supplier_status = True
            supplier_details.onhold_date = datetime.datetime.now().date()
        else:
            supplier_status = False
            supplier_details.onhold_date = None

        supplier_details.onhold = supplier_status
        supplier_details.save(update_fields=['onhold'])
        supplier_details.save(update_fields=['onhold_date'])

        return redirect('/suppliers')

    showsupplierdetails = False

    supplier_name = ""
    supplier_email = ""
    minimum_order = ""
    website_name = ""
    website_link = ""
    username = ""
    password = ""
    short_code = ""
    website_order_placement = ""
    onhold = ""
    onhold_date = ""
    contact_name = ""
    contact_email = ""
    contact_number = ""
    contact_position = ""
    last_stock_update=""
    stock_update_file_name=""

    if request.method == 'GET':
        supplier_name = request.GET.get('supplier_name')
        if not (supplier_name == None):
            showsupplierdetails = True

            supplier_details = Supplier_Details.objects.filter(supplier_name=supplier_name,disabled=False)
            for supp in supplier_details:
                supplier_name = supp.supplier_name
                supplier_email = supp.supplier_email
                minimum_order = supp.minimum_order
                website_name = supp.website_name
                website_link = supp.website_link
                username = supp.username
                password = supp.password
                short_code = supp.short_code
                website_order_placement = supp.website_order_placement
                onhold = supp.onhold
                onhold_date = supp.onhold_date
                contact_name = supp.contact_name
                contact_email = supp.contact_email
                contact_number = supp.contact_number
                contact_position = supp.contact_position
                last_stock_update=supp.last_stock_update
                stock_update_file_name=supp.last_stock_update_filename

    # Getting the on hold status of every supplier
    supplierdetails = {}
    supplier_details = Supplier_Details.objects.all()
    for temp in supplier_details:
        supplierdetails[temp.supplier_name] = {"name": temp.supplier_name, "status": temp.onhold,
                                               "onhold_date": temp.onhold_date}

    # For sorting the list
    List_of_suppliers = [(name, supplierdetails[name]['status'], supplierdetails[name]['onhold_date']) for name in
                         supplierdetails.keys()]
    list1 = list(map(list, zip(*List_of_suppliers)))
    if (len(list1) > 0):
        List_of_suppliers = zip(list1[0], list1[1], list1[2])
        List_of_suppliers = list(List_of_suppliers)
    List_of_suppliers = sorted(List_of_suppliers, key=lambda x: x[1], reverse=True)

    # Getting the supplier outofstock percentage

    # purchaseorder
    # orderline.objects.filter(instock)
    # findspotsordermanagement
    # SupplierNew.objects.filter()

    # select
    # sn.primarysupplier, count(sn.primarysupplier)
    # from public.purchaseorder_orderline ol, public.purchaseorder_purchaseorder
    # po, public.suppliers_suppliernew
    # sn
    # where
    # po.purchase_orderid = ol.purchase_orderid_id and po.submitted_date > '2019-10-28' and ol.qty != ol.instock and ol.order_line_id = sn.order_line_id
    # group
    # by
    # sn.primarysupplier
    #
    # select
    # sn.primarysupplier, count(sn.primarysupplier)
    # from public.purchaseorder_orderline ol, public.purchaseorder_purchaseorder
    # po, public.suppliers_suppliernew
    # sn
    # where
    # po.purchase_orderid = ol.purchase_orderid_id and po.submitted_date > '2019-10-28' and ol.order_line_id = sn.order_line_id
    # group
    # by
    # sn.primarysupplier

    return render(request, 'suppliers/suppliers.html', {"suppliers": True, "List_of_suppliers": List_of_suppliers,
                                                        "showsupplierdetails": showsupplierdetails,
                                                        "supplier_name": supplier_name,
                                                        "supplier_email": supplier_email,
                                                        "minimum_order": minimum_order, "website_name": website_name,
                                                        "website_link": website_link, "username": username,
                                                        "password": password, "short_code": short_code,
                                                        "website_order_placement": website_order_placement,
                                                        "onhold": onhold, "onhold_date": onhold_date,
                                                        "contact_name": contact_name, "contact_email": contact_email,
                                                        "contact_number": contact_number,
                                                        "contact_position": contact_position,"last_stock_update":last_stock_update,"stock_update_file_name":stock_update_file_name})


def get_list_of_urgent_orderids():
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)

    dict_pending_dispatched = {}
    try:
        db_order_pending_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=True,
                                                                        Cancelled__isnull=True,
                                                                        Uncommitted__isnull=True,
                                                                        delayed=False).exclude(
            order_id__contains='Alex')

        for temp in db_order_pending_dispatched:
            if (temp.invoice_date == "" or temp.invoice_date == None):
                dict_pending_dispatched[temp.order_id] = (temp.order_id, 0, temp.invoice_date)
            else:
                business_days = np.busday_count(temp.invoice_date, today_date)
                dict_pending_dispatched[temp.order_id] = (temp.order_id, str(business_days), temp.invoice_date)

    except:
        print("Something went wrong!")

    error_count_dispatch_pending = 0
    List_of_dispatched_pending = [(order, days, date) for order, days, date in dict_pending_dispatched.values()]
    list1 = list(map(list, zip(*List_of_dispatched_pending)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            if not (list1[1][index] == 0):
                list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 5):
                error_count_dispatch_pending += 1

        List_of_dispatched_pending = zip(list1[0], list1[1], list1[2])
        List_of_dispatched_pending = list(List_of_dispatched_pending)
    List_of_dispatched_pending = sorted(List_of_dispatched_pending, key=lambda x: x[1], reverse=True)

    list_of_urgent_orders = []
    for index in range(0, len(List_of_dispatched_pending)):
        order = List_of_dispatched_pending[index]
        order_id = order[0]
        days = order[1]
        if (int(days) >= 5):
            list_of_urgent_orders.append(order_id)

    return list_of_urgent_orders
