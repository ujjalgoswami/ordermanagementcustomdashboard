from wsgiref.util import FileWrapper

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date
import json
import requests
import numpy as np
from io import BytesIO
from xlsxwriter import Workbook
import pandas as pd
from django.contrib import messages
import os
from django.conf import settings

from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response, sendemail
from home.models import PendingDispatchOrderIDExceptions, PendingRefundsOrderIDExceptions

from netoapihook.models import OrderHistory
from purchaseorder.models import orderid_purchaseorderid,purchaseorder

@login_required
def index(request):
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)

    temp_list = pending_dispatched(today_date)
    error_count_dispatch_pending = temp_list[1]
    List_of_dispatched_pending = temp_list[0]

    temp_list = delayed_dispatched()
    List_of_delayed_dispatched = temp_list[0]
    error_count_delayed_dispatch = temp_list[1]

    temp_list = refunded()
    List_of_refunds_issued = temp_list[0]
    error_count_refund_issued = temp_list[1]

    temp_list = delayed_pending_dispatched(today_date)
    List_of_delayed_dispatched_pending = temp_list[0]
    error_count_delayed_dispatch_pending = temp_list[1]

    temp_list = dispatched()
    List_of_dispatched = temp_list[0]
    error_count_dispatch = temp_list[1]

    temp_list = to_be_refunded(today_date)
    List_of_refunds_pending = temp_list[0]
    error_count_refund_pending = temp_list[1]

    # For File download
    file_type_to_download = request.GET.get('download')
    if (file_type_to_download):
        list_of_order_ids = []
        list_of_business_days = []
        list_of_invoice_date = []

        if (file_type_to_download == 'dispatchedpending'):
            # subject = "Pending Dispatched Orders - FIND DASHBOARD"
            # body = "Hi, Please find the requested document in the attachment ."
            # receiver_email = "orders@findsports.com.au"
            path_to_attachment = os.path.abspath(os.path.dirname(__name__)) + "/Dispatched_Pending_Orders.xlsx"
            #
            # sendemail(subject, body, receiver_email, path_to_attachment, "Dispatched_Pending_Orders.xlsx",
            #           attachment=True)
            # messages.info(request, "File sent to " + str(receiver_email))
            # return redirect("/")

        elif (file_type_to_download == 'dispatchedpendingforced'):
            creatependingdispatchfile()
            subject = "Pending Dispatched Orders - FIND DASHBOARD"
            body = "Hi, Please find the requested document in the attachment ."
            receiver_email = "orders@findsports.com.au"
            path_to_attachment = os.path.abspath(os.path.dirname(__name__)) + "/Dispatched_Pending_Orders.xlsx"
            sendemail(subject, body, receiver_email, path_to_attachment, "Dispatched_Pending_Orders.xlsx",
                      attachment=True)
            messages.info(request, "File sent to " + str(receiver_email))
            return redirect("/")


        elif (file_type_to_download == 'delayeddispatchpending'):
            for index in range(0, len(List_of_delayed_dispatched_pending)):
                list_of_order_ids.append(List_of_delayed_dispatched_pending[index][0])
                list_of_business_days.append(List_of_delayed_dispatched_pending[index][1])
                try:
                    list_of_invoice_date.append(List_of_delayed_dispatched_pending[index][2])
                except:
                    list_of_invoice_date.append("")
            filename = "Delayed_Dispatched_Pending_Orders"

        elif (file_type_to_download == 'delayeddispatched'):

            for index in range(0, len(List_of_delayed_dispatched)):
                list_of_order_ids.append(List_of_delayed_dispatched[index][0])
                list_of_business_days.append(List_of_delayed_dispatched[index][1])
                try:
                    list_of_invoice_date.append(List_of_delayed_dispatched[index][2])
                except:
                    list_of_invoice_date.append("")
            filename = "Delayed_Dispatched_Orders"


        elif (file_type_to_download == 'dispatched'):

            for index in range(0, len(List_of_dispatched)):
                list_of_order_ids.append(List_of_dispatched[index][0])
                list_of_business_days.append(List_of_dispatched[index][1])
                try:
                    list_of_invoice_date.append(List_of_dispatched[index][2])
                except:
                    list_of_invoice_date.append("")
            filename = "Dispatched_Orders"
        elif (file_type_to_download == 'refunds'):

            for index in range(0, len(List_of_refunds_issued)):
                list_of_order_ids.append(List_of_refunds_issued[index][0])
                list_of_business_days.append(List_of_refunds_issued[index][1])
                try:
                    list_of_invoice_date.append(List_of_refunds_issued[index][2])
                except:
                    list_of_invoice_date.append("")
            filename = "Refunded_Orders"

        elif (file_type_to_download == 'refundspending'):

            for index in range(0, len(List_of_refunds_pending)):
                list_of_order_ids.append(List_of_refunds_pending[index][0])
                list_of_business_days.append(List_of_refunds_pending[index][1])
                try:
                    list_of_invoice_date.append(List_of_refunds_pending[index][2])
                except:
                    list_of_invoice_date.append("")
            filename = "Refund_Pending_Orders"

        if not (file_type_to_download == 'dispatchedpending'):
            columns = ['orderid', 'business_days', 'invoice_date']
            df = pd.DataFrame(columns=columns)
            df['orderid'] = list_of_order_ids
            df['business_days'] = list_of_business_days
            df['invoice_date'] = list_of_invoice_date

            response = HttpResponse(content_type='text/csv')

            response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'

            df.to_csv(path_or_buf=response, index=False)
            return response
        else:
            try:
                path_to_attachment = os.path.abspath(os.path.dirname(__name__)) + "/Dispatched_Pending_Orders.xlsx"
                wrapper = FileWrapper(open(path_to_attachment, 'rb'))
                response = HttpResponse(wrapper, content_type='application/force-download')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path_to_attachment)
                return response
            except Exception as e:
                return None

    List_of_dispatched_pending = List_of_dispatched_pending[0:15]
    List_of_dispatched = List_of_dispatched[0:15]
    List_of_refunds_issued = List_of_refunds_issued[0:15]
    List_of_refunds_pending = List_of_refunds_pending[0:15]

    List_of_delayed_dispatched = List_of_delayed_dispatched[0:15]
    List_of_delayed_dispatched_pending = List_of_delayed_dispatched_pending[0:15]

    return render(request, 'home/dashboard.html',
                  {"dashboard": True, "error_count_delayed_dispatch": error_count_delayed_dispatch,
                   "error_count_delayed_dispatch_pending": error_count_delayed_dispatch_pending,
                   "delayed_pending_dispatched_orders": List_of_delayed_dispatched_pending,
                   "delayed_dispatched_orders": List_of_delayed_dispatched,
                   "pending_dispatched_orders": List_of_dispatched_pending,
                   "error_count_dispatch": error_count_dispatch,
                   "error_count_dispatch_pending": error_count_dispatch_pending,
                   "error_count_refund_issued": error_count_refund_issued,
                   "error_count_refund_pending": error_count_refund_pending, "dispatched_orders": List_of_dispatched,
                   "orders": False, "stocklevel": False, "missing_tracking_ids": 0,
                   "pending_issues": 0, "issues": {}, "refunded_orders": List_of_refunds_issued, "today": today_date,
                   "not_refunded_orders": List_of_refunds_pending})


def delayed_dispatched():
    dict_delayed_dispatched = {}
    try:
        db_order_delayed_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=False,
                                                                        delayed=True).exclude(order_id__contains='Alex')

        for temp in db_order_delayed_dispatched:
            if (temp.shipped_date == "" or temp.shipped_date == None):
                dict_delayed_dispatched[temp.order_id] = (temp.order_id, 0, temp.invoice_date)
            else:
                business_days = np.busday_count(temp.invoice_date, temp.shipped_date)
                dict_delayed_dispatched[temp.order_id] = (temp.order_id, str(business_days), temp.invoice_date)
    except:
        print("Something went wrong!")

    error_count_delayed_dispatch = 0
    List_of_delayed_dispatched = [(order, days, date) for order, days, date in dict_delayed_dispatched.values()]
    list1 = list(map(list, zip(*List_of_delayed_dispatched)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            # print("h2",list1[1])
            list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 7):
                error_count_delayed_dispatch += 1

        List_of_delayed_dispatched = zip(list1[0], list1[1], list1[2])
        List_of_delayed_dispatched = list(List_of_delayed_dispatched)
    List_of_delayed_dispatched = sorted(List_of_delayed_dispatched, key=lambda x: x[1], reverse=True)

    return [List_of_delayed_dispatched, error_count_delayed_dispatch]


def delayed_pending_dispatched(today_date):
    dict_delayed_pending_dispatched = {}
    try:
        db_order_delayed_pending_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=True,
                                                                                Cancelled__isnull=True,
                                                                                Uncommitted__isnull=True,
                                                                                delayed=True).exclude(
            order_id__contains='Alex')

        for temp in db_order_delayed_pending_dispatched:
            if (temp.invoice_date == "" or temp.invoice_date == None):
                dict_delayed_pending_dispatched[temp.order_id] = (temp.order_id, 0, temp.invoice_date)
            else:
                business_days = np.busday_count(temp.invoice_date, today_date)
                dict_delayed_pending_dispatched[temp.order_id] = (temp.order_id, str(business_days), temp.invoice_date)
    except:
        print("Something went wrong!")

    error_count_delayed_dispatch_pending = 0
    List_of_delayed_dispatched_pending = [(order, days, date) for order, days, date in
                                          dict_delayed_pending_dispatched.values()]
    list1 = list(map(list, zip(*List_of_delayed_dispatched_pending)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            if not (list1[1][index] == 0):
                list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 7):
                error_count_delayed_dispatch_pending += 1

        List_of_delayed_dispatched_pending = zip(list1[0], list1[1], list1[2])
        List_of_delayed_dispatched_pending = list(List_of_delayed_dispatched_pending)
    List_of_delayed_dispatched_pending = sorted(List_of_delayed_dispatched_pending, key=lambda x: x[1], reverse=True)

    return [List_of_delayed_dispatched_pending, error_count_delayed_dispatch_pending]


def to_be_refunded(today_date):

    dict_toberefunded = {}
    try:

        #Not including order ids in Exception table
        pendingrefundexceptions=PendingRefundsOrderIDExceptions.objects.all()
        list_of_order_id_exceptions = [result.order_id for result in pendingrefundexceptions]


        db_order_not_refunded = OrderHistory.objects.all().filter(Uncommitted__isnull=False, Cancelled__isnull=True).exclude(order_id__in=list_of_order_id_exceptions)

        for temp in db_order_not_refunded:

            if (temp.shipped_date == None or temp.shipped_date < temp.Uncommitted):
                business_days = np.busday_count(temp.Uncommitted, today_date)

                dict_toberefunded[temp.order_id] = (
                    temp.order_id, str(business_days).replace(", 0:00:00", ""), temp.invoice_date)
    except:
        print("Something went wrong!")

    error_count_refund_pending = 0
    List_of_refunds_pending = [(order, days, date) for order, days, date in dict_toberefunded.values()]
    list1 = list(map(list, zip(*List_of_refunds_pending)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 7):
                error_count_refund_pending += 1
        List_of_refunds_pending = zip(list1[0], list1[1], list1[2])
        List_of_refunds_pending = list(List_of_refunds_pending)

    List_of_refunds_pending = sorted(List_of_refunds_pending, key=lambda x: x[1], reverse=True)

    return [List_of_refunds_pending, error_count_refund_pending]


def refunded():
    dict_refunded = {}
    try:
        db_order_refunded = OrderHistory.objects.all().filter(Uncommitted__isnull=False, Cancelled__isnull=False)

        for temp in db_order_refunded:
            business_days = np.busday_count(temp.Uncommitted, temp.Cancelled)
            dict_refunded[temp.order_id] = (temp.order_id, str(business_days), temp.invoice_date)
    except:
        print("Something went wrong!")

    error_count_refund_issued = 0
    List_of_refunds_issued = [(order, days, date) for order, days, date in dict_refunded.values()]
    list1 = list(map(list, zip(*List_of_refunds_issued)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            # print(list1[1][index])
            list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 7):
                error_count_refund_issued += 1

        List_of_refunds_issued = zip(list1[0], list1[1], list1[2])
        List_of_refunds_issued = list(List_of_refunds_issued)

    List_of_refunds_issued = sorted(List_of_refunds_issued, key=lambda x: x[1], reverse=True)

    return [List_of_refunds_issued, error_count_refund_issued]


def dispatched():
    dict_dispatched = {}
    try:
        db_order_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=False, delayed=False).exclude(
            order_id__contains='Alex')

        for temp in db_order_dispatched:
            # print(temp.shipped_date,temp.invoice_date)
            if (temp.shipped_date == "" or temp.shipped_date == None):
                dict_dispatched[temp.order_id] = (temp.order_id, 0, temp.invoice_date)
            else:
                if(temp.invoice_date==None):
                    business_days=0
                else:
                    business_days = np.busday_count(temp.invoice_date, temp.shipped_date)
                dict_dispatched[temp.order_id] = (temp.order_id, str(business_days), temp.invoice_date)
    except:
        print("Something went wrong!")

    error_count_dispatch = 0
    List_of_dispatched = [(order, days, date) for order, days, date in dict_dispatched.values()]
    list1 = list(map(list, zip(*List_of_dispatched)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 7):
                error_count_dispatch += 1

        List_of_dispatched = zip(list1[0], list1[1], list1[2])
        List_of_dispatched = list(List_of_dispatched)
    List_of_dispatched = sorted(List_of_dispatched, key=lambda x: x[1], reverse=True)

    return [List_of_dispatched, error_count_dispatch]


def pending_dispatched(today_date):
    dict_pending_dispatched = {}
    try:

        #Not including order ids in Exception table
        pendingdispatchedexceptions=PendingDispatchOrderIDExceptions.objects.all()
        pendingrefundexceptions = PendingRefundsOrderIDExceptions.objects.all()

        list_of_order_id_exceptions = [result.order_id for result in pendingdispatchedexceptions]
        list_of_order_id_exceptions2 = [result.order_id for result in pendingrefundexceptions]

        db_order_pending_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=True,
                                                                        Cancelled__isnull=True,
                                                                        Uncommitted__isnull=True,
                                                                        delayed=False).exclude(
            order_id__contains='Alex').exclude(order_id__in=list_of_order_id_exceptions).exclude(order_id__in=list_of_order_id_exceptions2)



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
            if (temp >= 7):
                error_count_dispatch_pending += 1

        List_of_dispatched_pending = zip(list1[0], list1[1], list1[2])
        List_of_dispatched_pending = list(List_of_dispatched_pending)
    List_of_dispatched_pending = sorted(List_of_dispatched_pending, key=lambda x: x[1], reverse=True)

    return [List_of_dispatched_pending, error_count_dispatch_pending]
def creatependingdispatchfile():
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)

    temp_list = pending_dispatched(today_date)
    error_count_dispatch_pending = temp_list[1]
    List_of_dispatched_pending = temp_list[0]



    list_of_order_ids = []
    list_of_business_days = []
    list_of_invoice_date = []


    list_of_sku = []

    # for dataframe
    list_of_product_name = []
    list_of_qty = []
    list_of_shippingoption = []
    list_of_sales_channel = []
    list_of_order_status = []
    list_of_grandtotal = []
    list_of_shipping_total = []
    list_of_order_id_new = []
    list_of_business_days_new = []
    list_of_invoice_date_new = []

    for index in range(0, len(List_of_dispatched_pending)):
        list_of_order_ids.append(List_of_dispatched_pending[index][0])
        list_of_business_days.append(List_of_dispatched_pending[index][1])
        try:
            list_of_invoice_date.append(List_of_dispatched_pending[index][2])
        except:
            list_of_invoice_date.append("")

    purchaseorders=orderid_purchaseorderid.objects.filter(order_id__in=list_of_order_ids)
    list_of_purchase_order_ids=[]
    dict_orderid_purchase_id={}

    for temp in purchaseorders:
        purchaseid=getattr(temp.purchase_orderid, 'purchase_orderid')
        orderid=temp.order_id
        dict_orderid_purchase_id[orderid]=purchaseid
        list_of_purchase_order_ids.append(purchaseid)

    dict_purchaseorderid_trackingid={}
    dict_purchaseorderid_alias = {}

    porderdetails=purchaseorder.objects.filter(purchase_orderid__in=list_of_purchase_order_ids)
    for temp2 in porderdetails:
        temp_dict={}
        trackingid=temp2.tracking_id
        purchaseorderid = temp2.purchase_orderid
        dict_purchaseorderid_trackingid[purchaseorderid]=trackingid

        temp_dict['alias']=temp2.alias
        temp_dict['received_date'] = temp2.received_date
        temp_dict['internal_notes'] = temp2.internal_notes

        dict_purchaseorderid_alias[purchaseorderid]=temp_dict


    filename = "Dispatched_Pending_Orders"

    list_of_rejected_order_status=['Pick','Cancelled','Quote','New']

    for index in range(0, len(list_of_order_ids)):
        #Including all orders even with 0 business days(Ordered today)
        if (list_of_business_days[index] >= 0):
            order_id = list_of_order_ids[index]
            response_temp = api_order_response({"OrderID": order_id}, None, None)
            temp_list = response_temp['Order']

            for temp in temp_list:
                list_of_orderlines = temp['OrderLine']
                for single_order_line in list_of_orderlines:

                    order_status = temp['OrderStatus']

                    if not(order_status in list_of_rejected_order_status):
                        list_of_order_status.append(order_status)

                        list_of_order_id_new.append(order_id)
                        list_of_business_days_new.append(list_of_business_days[index])

                        list_of_invoice_date_new.append(str(list_of_invoice_date[index]))

                        product_name = single_order_line['ProductName']
                        list_of_product_name.append(product_name)

                        qty = single_order_line['Quantity']
                        list_of_qty.append(qty)

                        sku = single_order_line['SKU']
                        list_of_sku.append(sku)

                        shippingoption = temp['ShippingOption']
                        list_of_shippingoption.append(shippingoption)

                        sales_channel = temp['SalesChannel']
                        list_of_sales_channel.append(sales_channel)



                        grandtotal = temp['GrandTotal']
                        list_of_grandtotal.append(grandtotal)

                        shipping_total = temp['ShippingTotal']
                        list_of_shipping_total.append(shipping_total)

                    # send the list of sku to product api to fetch the primary supplier

    response_product = api_product_response({"SKU": list_of_sku}, ["PrimarySupplier", "SKU"], None)
    temp_prod_response_list = response_product['Item']

    dict_sku_primary_supplier = {}
    for temp in temp_prod_response_list:
        dict_sku_primary_supplier[temp['SKU']] = temp['PrimarySupplier']

    list_of_PrimarySupplier = [""] * len(list_of_sku)
    for index in range(0, len(list_of_sku)):
        sku = list_of_sku[index]
        list_of_PrimarySupplier[index] = dict_sku_primary_supplier[sku]

    columns = ['orderid', 'business_days', 'invoice_date', 'Product Name', 'qty', 'SKU', 'shipping option','sales channel', 'order status', 'grand total', 'shipping total', 'primary supplier','Comments','Purchase Order','Received Date','Internal Notes']

    return create_excel(dict_orderid_purchase_id,dict_purchaseorderid_trackingid,columns,list_of_order_id_new, list_of_business_days_new, list_of_invoice_date_new, list_of_product_name,
                 list_of_qty, list_of_sku, list_of_shippingoption, list_of_sales_channel, list_of_order_status,
                 list_of_grandtotal, list_of_shipping_total, list_of_PrimarySupplier,dict_purchaseorderid_alias)




def create_excel(dict_orderid_purchase_id,dict_purchaseorderid_trackingid,columns,list_of_order_id_new,list_of_business_days_new,list_of_invoice_date_new,list_of_product_name,list_of_qty,list_of_sku,list_of_shippingoption,list_of_sales_channel,list_of_order_status,list_of_grandtotal,list_of_shipping_total,list_of_PrimarySupplier,dict_purchaseorderid_alias):

    output = BytesIO()

    wb = Workbook('Dispatched_Pending_Orders.xlsx')

    ws = wb.add_worksheet('Sheet1')

    #Setting up the header!
    for index in range(0,len(columns)):
        ws.write(0, index, columns[index],wb.add_format({'bold': True, 'font_color': '', 'font_size': '14', 'font_name': 'Arial'}))

    for index in range(0,len(list_of_order_id_new)):


        cell_format_out_of_stock = wb.add_format()
        cell_format_out_of_stock.set_pattern(1)
        comment=""
        bgcolor=""
        if(int(list_of_business_days_new[index])>5):
            bgcolor='#e83a3a'


        if(list_of_PrimarySupplier[index]=='FIND_Imports'):
            comment="Find Import Product"
            if(len(bgcolor)==0):
                bgcolor='#5DADE2'
        else:
            if(str(list_of_order_id_new[index]) in dict_orderid_purchase_id):
                if(dict_orderid_purchase_id[list_of_order_id_new[index]] in dict_purchaseorderid_trackingid):
                    if(list_of_order_id_new[index] in dict_orderid_purchase_id and dict_purchaseorderid_trackingid[dict_orderid_purchase_id[list_of_order_id_new[index]]] == "NA"):
                        comment="Tracking ID not found"
                        if (len(bgcolor) == 0):
                            bgcolor='#ffcc9c'
                    elif(list_of_order_id_new[index] in dict_orderid_purchase_id and dict_purchaseorderid_trackingid[dict_orderid_purchase_id[list_of_order_id_new[index]]] != "NA"):
                        comment="Purchase order found!.Search orderid in FindDashboard search bar to track related Purchase Orders"
                        if (len(bgcolor) == 0):
                            bgcolor='#00B200'
                    else:
                        comment = "Tracking ID not found"
                        if (len(bgcolor) == 0):
                            bgcolor='#e83a3a'
                else:
                    comment="Purchase ID not found"
                    if (len(bgcolor) == 0):
                        bgcolor='#e83a3a'
            else:
                comment="Cannot connect OrderID to a Purchase id"
                if (len(bgcolor) == 0):
                    bgcolor='#ffff00'


        cell_format_out_of_stock.set_bg_color(bgcolor)

        ws.write(1+index,0 ,list_of_order_id_new[index],cell_format_out_of_stock)
        ws.write(1 + index, 1, list_of_business_days_new[index], cell_format_out_of_stock)
        ws.write(1 + index, 2, str(list_of_invoice_date_new[index]), cell_format_out_of_stock)
        ws.write(1 + index, 3, list_of_product_name[index], cell_format_out_of_stock)
        ws.write(1 + index, 4, list_of_qty[index], cell_format_out_of_stock)
        ws.write(1 + index, 5, list_of_sku[index], cell_format_out_of_stock)
        ws.write(1 + index, 6, list_of_shippingoption[index], cell_format_out_of_stock)
        ws.write(1 + index, 7, list_of_sales_channel[index], cell_format_out_of_stock)
        ws.write(1 + index, 8, list_of_order_status[index], cell_format_out_of_stock)
        ws.write(1 + index, 9, list_of_grandtotal[index], cell_format_out_of_stock)
        ws.write(1 + index, 10, list_of_shipping_total[index], cell_format_out_of_stock)
        ws.write(1 + index, 11, list_of_PrimarySupplier[index], cell_format_out_of_stock)
        ws.write(1 + index, 12, comment, cell_format_out_of_stock)
        try:
            alias=dict_purchaseorderid_alias[dict_orderid_purchase_id[list_of_order_id_new[index]]]['alias']
        except:
            alias=""

        ws.write(1 + index, 13, alias, cell_format_out_of_stock)
        try:
            received_date=str(dict_purchaseorderid_alias[dict_orderid_purchase_id[list_of_order_id_new[index]]]['received_date'])
        except:
            received_date=""

        ws.write(1 + index, 14, received_date, cell_format_out_of_stock)

        try:
            internal_notes=dict_purchaseorderid_alias[dict_orderid_purchase_id[list_of_order_id_new[index]]]['internal_notes']
        except:
            internal_notes=""
        ws.write(1 + index, 15, internal_notes, cell_format_out_of_stock)

    wb.close()


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage('assets/datafiles')
        if os.path.isfile('assets/datafiles/neto_refunds.csv'):
            os.remove('assets/datafiles/neto_refunds.csv')
        filename = fs.save('neto_refunds.csv', myfile)
        df=pd.read_csv("assets/datafiles/neto_refunds.csv")

        list_of_refund_notes=list(df["Refund Notes"])
        list_of_refund_orderids=list(df["Order ID"])

        batch=[]
        # Looking for existing data for today's stockupdate
        #  list_of_already_refunded_orderids = [result.order_id for result in PendingRefundsOrderIDExceptions_objects]
        #     print(list_of_already_refunded_orderids)
        #     print("Refund data for today already exists")


            #None exists creating the data

        for index in range(0,len(list_of_refund_orderids)):
            orderid=list_of_refund_orderids[index]
            refund_note=list_of_refund_notes[index]
            print(index)
            try:
                PendingDispatchOrderIDExceptions_objects = PendingDispatchOrderIDExceptions.objects.get(
                    order_id=orderid)
            except:
                query = PendingDispatchOrderIDExceptions(order_id=orderid,comments=refund_note)
                batch.append(query)

        batch_size = 50
        PendingRefundsOrderIDExceptions.objects.bulk_create(batch, batch_size)
        # except:
        #     # Inserting new stats
        #
        #     stockupdatestats = stockupdate(
        #         supplier_name=supplier_name_db,
        #         run_date=run_date,
        #         run_status=run_status,
        #         oos_items=oos_items,
        #         prev_instock=prev_instock,
        #         new_instock=new_instock,
        #         time_taken=time_taken,
        #         stock_update_approved=stock_update_approved,
        #         comments=comments
        #     )
        #     stockupdatestats.save()


        return redirect('/')
    return redirect('/')