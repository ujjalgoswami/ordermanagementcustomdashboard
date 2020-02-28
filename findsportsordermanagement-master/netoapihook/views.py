from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from xml.etree import ElementTree as ET
import json
import requests

from netoapihook.models import OrderHistory
from django.core.mail import send_mail
from django.conf import settings

from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response


def insert_data(order_status, order_id, current_time, action):
    try:
        # Trying to Updating
        db_order = OrderHistory.objects.get(order_id=order_id)
    except:
        # inserting new value
        db_order = OrderHistory(order_id=order_id)

    invo_date = get_invoice_date(order_id)['DateInvoiced']
    sales_channel = get_invoice_date(order_id)['SalesChannel']

    if (invo_date == "" or invo_date == None):
        invo_date = None

    if (sales_channel == "" or sales_channel == None):
        sales_channel = None

    db_order.invoice_date = invo_date

    db_order.sales_channel = sales_channel

    if (order_status == "Pack"):
        db_order.Pack = current_time

    elif (order_status == "Pending Pickup"):
        db_order.Pending_Pickup = current_time

    elif (order_status == "Pending Dispatch"):
        db_order.Pending_Dispatch = current_time

    elif (order_status == "Dispatched"):
        db_order.Dispatched = current_time

    elif (order_status == "Cancelled"):
        db_order.Cancelled = current_time

    elif (order_status == "Uncommitted"):
        db_order.Uncommitted = current_time

    elif (order_status == "Pick"):
        db_order.Pick = current_time

    elif (order_status == "Backorder Approved"):
        db_order.Backorder_Approved = current_time

    elif (order_status == "New Backorder"):
        db_order.New_Backorder = current_time

    elif (order_status == "On Hold"):
        db_order.On_Hold = current_time

    elif (order_status == "New"):
        db_order.New = current_time

    elif (order_status == "Quote"):
        db_order.Quote = current_time

    if (action == "update"):
        db_order.save(update_fields=['Pack'])
        db_order.save(update_fields=['Pending_Pickup'])
        db_order.save(update_fields=['Pending_Dispatch'])
        db_order.save(update_fields=['Dispatched'])
        db_order.save(update_fields=['Cancelled'])
        db_order.save(update_fields=['Uncommitted'])
        db_order.save(update_fields=['Backorder_Approved'])
        db_order.save(update_fields=['New_Backorder'])
        db_order.save(update_fields=['On_Hold'])
        db_order.save(update_fields=['New'])
        db_order.save(update_fields=['Pick'])
        db_order.save(update_fields=['Quote'])
        db_order.save(update_fields=['invoice_date'])
        db_order.save(update_fields=['sales_channel'])
    else:
        db_order.save()


@csrf_exempt
def index(request):
    if request.method == "POST":
        xml_request = request.body
    else:
        xml_request = "Invalid"

    if not (xml_request == "Invalid"):

        xml_request = xml_request.strip()
        current_time = ET.fromstring(xml_request).find('CurrentTime').text
        current_time = current_time.split(" ")[0]
        order_id = ET.fromstring(xml_request).find('Order/OrderID').text
        order_status = ET.fromstring(xml_request).find('Order/OrderStatus').text

        order_id_exists = OrderHistory.objects.filter(order_id__exact=order_id).count()

        if (order_id_exists > 0):
            # An order exists and needs to be updated!

            insert_data(order_status, order_id, current_time, action="update")

        else:
            # New order

            insert_data(order_status, order_id, current_time, action="new")

        return HttpResponse('<h1>API SUCCESS</h1>')

    else:
        return HttpResponseNotFound('<h1>INVALID REQUEST</h1>')


def get_invoice_date(order_id):
    dict_input_filter = {"OrderID": order_id}
    json1_data = api_order_response(dict_input_filter, ['DateInvoiced', 'SalesChannel'])

    dict_of_order_details = json1_data['Order'][0]

    return dict_of_order_details
