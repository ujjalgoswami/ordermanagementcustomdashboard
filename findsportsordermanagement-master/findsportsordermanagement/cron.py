from django_cron import CronJobBase, Schedule
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from xml.etree import ElementTree as ET
import json
from datetime import date
from xlsxwriter import Workbook
import requests
import pandas as pd
from customers.models import Customers
from home.views import pending_dispatched, creatependingdispatchfile
from netoapihook.models import OrderHistory
from django.core.mail import send_mail
from django.conf import settings

from purchaseorder.models import orderid_purchaseorderid,purchaseorder
from suppliers.models import SupplierNew
from suppliers.views import get_list_of_urgent_orderids
from findsportsordermanagement.initialparameters import order_headers,product_headers,url,api_order_response,api_product_response
from timebomb.views import autocreatetimebombfile


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 30 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'my_app.my_cron_job'    # a unique code

    def do(self):
        print("Insert backorder called!")
        #insert_backorders()
        print("Insert Happy orders called")
        insert_happy_customers()
        print("Create new pending dispatch file!")
        creatependingdispatchfile()
        print("Invoked!")

        print("Creating timebomb file")
        autocreatetimebombfile()
        pass    # do your thing here






def insert_backorders():
    temp_response=api_order_response({"OrderStatus":"New Backorder"},["OrderID"])
    response=temp_response['Order']


    list_of_newbackorder_order_ids=[]
    for order in response:
        list_of_newbackorder_order_ids.append(order['OrderID'])

    print(list_of_newbackorder_order_ids)
    insert_data(list_of_newbackorder_order_ids)

def insert_happy_customers():
    # Getting all orders which are shipped
    shipped_customers = OrderHistory.objects.all().filter(shipped_date__isnull=False, invoice_date__isnull=False)

    # list of orderids which have been shipped in 7 days or less
    list_of_happy_order_ids = []

    dict_of_order_id = {}
    # Looping through all shipped orders
    for shipped in shipped_customers:
        # Calculating the number of days taken to ship
        number_of_days = shipped.shipped_date - shipped.invoice_date
        # Handling special case of instore pickups
        if (str(number_of_days) == "0:00:00"):
            # instore pickups handle it
            number_of_days = 0

        else:
            number_of_days = int(
                str(number_of_days).replace("days, 0: 00:00", "").replace(" day, 0:00:00", "").replace(" days, 0:00:00",
                                                                                                       ""))

        orderid = shipped.order_id
        sales_channel = shipped.sales_channel

        if (number_of_days <= 7):
            list_of_happy_order_ids.append(orderid)
            tempdict = {}
            tempdict['order_id'] = orderid
            tempdict['number_of_days'] = number_of_days
            tempdict['invoiced_date'] = shipped.invoice_date
            tempdict['shipped_date'] = shipped.shipped_date
            tempdict['sales_channel'] = sales_channel
            dict_of_order_id[orderid] = tempdict

    # Getting those customers which have had their order shipped in 7 days or less
    shipped_customers = Customers.objects.filter(order_id__in=list_of_happy_order_ids)
    result_ids = [result.order_id for result in shipped_customers]
    list_of_order_ids_not_found = [None if order_id in result_ids else order_id for order_id in list_of_happy_order_ids]

    # Removing all null values and keeping only those order ids which are not found in the customer table
    list_of_order_ids_not_found = [i for i in list_of_order_ids_not_found if i]

    if (len(list_of_order_ids_not_found) > 0):
        # Inserting values for those order_ids which are new and not yet entered in the customer table
        for index in range(0, len(list_of_order_ids_not_found)):
            orderid = list_of_order_ids_not_found[index]
            customer_details = api_order_response({"OrderID": list_of_happy_order_ids[index]}, None)
            first_name = customer_details['Order'][0]['ShipFirstName']
            last_name = customer_details['Order'][0]['ShipLastName']
            email = customer_details['Order'][0]['Email']

            shipped_customers = Customers(order_id=str(orderid), first_name=first_name, last_name=last_name,
                                          email=email)
            shipped_customers.save()


def insert_data(list_of_order_ids=None):
    if(list_of_order_ids==None):
        list_of_order_ids = get_list_of_urgent_orderids()

    list_of_order_line_ids=[]

    orders = SupplierNew.objects.filter(order_id__in=list_of_order_ids)

    result_ids = [result.order_id for result in orders]

    list_of_order_ids_not_found = [None if order_id in result_ids else order_id for order_id in list_of_order_ids]
    list_of_order_ids_not_found = [x for x in list_of_order_ids_not_found if x is not None]


    dict_of_orderline_id_details={}

    if (len(list_of_order_ids_not_found) > 0):
        for index in range(0, len(list_of_order_ids_not_found)):
            print(index)

            temp_dict = get_supplier_details(list_of_order_ids_not_found[index])[0]


            for orderline in temp_dict:
                dict_of_orderline_id_details[orderline]={"Orderid":temp_dict[orderline]['Orderid'],"SKU":temp_dict[orderline]['SKU'],"PrimarySupplier":temp_dict[orderline]['PrimarySupplier']}


    orders = SupplierNew.objects.filter(order_line_id__in=list_of_order_line_ids)

    batch = []
    for orderlineid in dict_of_orderline_id_details.keys():

        order_id=dict_of_orderline_id_details[orderlineid]['Orderid']
        sku = dict_of_orderline_id_details[orderlineid]['SKU']
        primarysupplier = dict_of_orderline_id_details[orderlineid]['PrimarySupplier']


        query = SupplierNew(order_line_id=orderlineid,order_id=str(order_id), sku=sku, primarysupplier=primarysupplier)
        batch.append(query)

    batch_size = 100
    SupplierNew.objects.bulk_create(batch, batch_size)


def get_supplier_details(order_id):
    order = api_order_response({'OrderID': order_id}, ['OrderLine'])
    list_of_orderlines = order['Order'][0]['OrderLine']
    list_of_skus = []
    list_of_order_line_ids=[]
    for index in range(0, len(list_of_orderlines)):
        list_of_skus.append(list_of_orderlines[index]['SKU'])
        list_of_order_line_ids.append(list_of_orderlines[index]['OrderLineID'])

    product_details = api_product_response({'SKU': list_of_skus}, ['PrimarySupplier'])['Item']

    dict_sku_supplier={}
    for product in product_details:
        dict_sku_supplier[product['SKU']]=product['PrimarySupplier']

    dict_order_line_id_sku={}
    for temp in list_of_orderlines:
        temp_dict={}
        temp_dict['SKU']=temp['SKU']
        temp_dict['PrimarySupplier'] = dict_sku_supplier[temp['SKU']]
        temp_dict['Orderid'] = order_id
        dict_order_line_id_sku[temp['OrderLineID']]=temp_dict


    return [dict_order_line_id_sku,list_of_order_line_ids]



