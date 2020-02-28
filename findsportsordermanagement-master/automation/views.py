from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
import json

from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response
from home.views import to_be_refunded, pending_dispatched

from netoapihook.models import OrderHistory
from purchaseorder.models import purchaseorder, purchaseorder_details
from purchaseorder.views import viewPendingSubmitCreatedPurchaseOrders
from refunds.views import purchaseorderoutofstockrefunds
from suppliers.models import Supplier_Details
from datetime import date

from trackingid.views import trackingpending


def index(request):
    return HttpResponse("<h1>Selenium Running</h1>")


def getnotifications(request):
    dict_notifications = {}

    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)

    suppliers = Supplier_Details.objects.filter(onhold=True)

    dict_suppliers_on_hold = {}

    for sup in suppliers:
        dict_suppliers_on_hold[sup.supplier_name] = {"Name": sup.supplier_name, "On Hold Date": sup.onhold_date}

    number_of_refunds_pending = to_be_refunded(today_date)[1]

    number_of_dispatch_pending = pending_dispatched(today_date)[1]

    list_of_submit_pending = viewPendingSubmitCreatedPurchaseOrders()

    purchaseorderrefunds = purchaseorderoutofstockrefunds()

    List_of_tracking_pending = trackingpending()

    dict_notifications["Suppliers"] = dict_suppliers_on_hold
    dict_notifications["RefundsPending"] = number_of_refunds_pending
    dict_notifications["DispatchPending"] = number_of_dispatch_pending
    dict_notifications["PurchaseOrderPendingSubmit"] = list_of_submit_pending
    dict_notifications["Purchaseorderrefunds"] = purchaseorderrefunds
    dict_notifications["PurchaseOrderTrackingPending"] = List_of_tracking_pending

    return JsonResponse(dict_notifications, json_dumps_params={'indent': 2})


def undispatchedorders(request):
    dict_orders = {}
    list_of_order_ids = []

    db_order_not_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=True, Cancelled__isnull=True,
                                                                invoice_date__isnull=False).exclude(
        order_id__contains='Alex')

    for order in db_order_not_dispatched:
        list_of_order_ids.append(order.order_id)

    dict_orders['Orders'] = list_of_order_ids

    return JsonResponse(dict_orders, json_dumps_params={'indent': 2})


def stock_update_supplier_details(request):
    dict_supp = {}
    list_of_supplier_details = []

    brandscope_suppliers_objects = Supplier_Details.objects.all().filter(stock_update_buy_plan_id__isnull=False)
    supp_all_dict = {}
    for supp in brandscope_suppliers_objects:
        temp_dict={}
        temp_dict['Name']=supp.supplier_name
        temp_dict['BuyPlanID'] = supp.stock_update_buy_plan_id
        temp_dict['URL'] = supp.stock_update_url
        temp_dict['ShortCode'] = supp.short_code
        temp_dict['BrandName'] = supp.stock_update_brand_name

        supp_all_dict[supp.supplier_name]=temp_dict

    list_of_supplier_details.append(supp_all_dict)

    dict_supp['Suppliers'] = list_of_supplier_details

    return JsonResponse(dict_supp, json_dumps_params={'indent': 2})

def dispatchedorders(request):
    dict_dispatched = {}
    list_of_order_ids = []

    db_order_dispatched = OrderHistory.objects.all().filter(shipped_date__isnull=False, delayed=False).exclude(
        order_id__contains='Alex')

    for order in db_order_dispatched:
        list_of_order_ids.append(order.order_id)
    dict_dispatched['Orders'] = list_of_order_ids

    return JsonResponse(dict_dispatched, json_dumps_params={'indent': 2})


@csrf_exempt
def setdispathedorders(request):
    if request.method == "POST":
        post_request = request.body

        api_key = json.loads(post_request)['apikey']
        if (api_key == "findsportsapikey12345"):
            dist_of_orders = json.loads(post_request)['orders']

            for key in dist_of_orders:
                if (dist_of_orders[key] == 'partialrefund'):
                    # setting dispatch date as cancelled date
                    db_order = OrderHistory.objects.all().filter(order_id=key)
                    dispatched_date = None
                    for temp in db_order:
                        dispatched_date = temp.Dispatched

                    # Updating cancelled date as the dispatched date
                    db_order2 = OrderHistory.objects.get(order_id=key)
                    db_order2.Cancelled = dispatched_date
                    db_order2.save(update_fields=['Cancelled'])

                elif (dist_of_orders[key] == 'dropshipped'):
                    # Set the shipped date as invoice date as customer has requested no shipping
                    dict_input_filter = {"OrderID": key}

                    # Fetching invoice id from neto
                    json1_data = api_order_response(dict_input_filter, ["DateInvoiced", "OrderID"])
                    db_order = OrderHistory.objects.get(order_id=key)
                    db_order.shipped_date = json1_data['Order'][0]['DateInvoiced']
                    db_order.is_dropshipped=True
                    db_order.save(update_fields=['shipped_date'])
                    db_order.save(update_fields=['is_dropshipped'])

                elif (dist_of_orders[key] == 'clickncollect'):
                    # Set the shipped date as invoice date as customer has requested no shipping
                    dict_input_filter = {"OrderID": key}

                    # Fetching invoice id from neto
                    json1_data = api_order_response(dict_input_filter, ["DateInvoiced", "OrderID"])
                    db_order = OrderHistory.objects.get(order_id=key)
                    db_order.shipped_date = json1_data['Order'][0]['DateInvoiced']
                    db_order.save(update_fields=['shipped_date'])

                elif (isinstance(dist_of_orders[key], list)):
                    print(dist_of_orders[key])
                    db_order = OrderHistory.objects.get(order_id=key)

                    if not (dist_of_orders[key][0] == 'Not Lodged' or dist_of_orders[key][0] == ''):
                        db_order.shipped_date = dist_of_orders[key][0]
                        db_order.save(update_fields=['shipped_date'])
                        db_order.save(update_fields=['delayed'])
                    else:
                        db_order.delayed = dist_of_orders[key][1]
                        db_order.save(update_fields=['delayed'])


                elif not (dist_of_orders[key] == 'Not Lodged' or dist_of_orders[key] == ''):
                    db_order = OrderHistory.objects.get(order_id=key)
                    db_order.shipped_date = dist_of_orders[key]
                    db_order.save(update_fields=['shipped_date'])

            return HttpResponse("<h1>Post Received</h1>")
        else:
            return HttpResponse("<h1>Invalid Post</h1>")


    else:
        return HttpResponse("<h1>Invalid Post</h1>")


@csrf_exempt
def setpurchaseorders(request):
    if request.method == "POST":
        post_request = request.body

        api_key = json.loads(post_request)['apikey']
        if (api_key == "findsportsapikey12345"):
            dist_of_purchase_orders = json.loads(post_request)['purchaseorders']

            for pid in dist_of_purchase_orders:

                if (len(dist_of_purchase_orders[pid]) > 0):
                    purchase_id = pid
                    supplier_name = dist_of_purchase_orders[pid]['supplier_name']
                    tracking_number = dist_of_purchase_orders[pid]['tracking_number']
                    if (str(tracking_number) == "nan" or str(tracking_number) == "nil"):
                        tracking_number = "NA"

                    courier = dist_of_purchase_orders[pid]['courier']
                    if (str(courier) == "nan" or str(courier) == "nil"):
                        courier = "NA"

                    date = dist_of_purchase_orders[pid]['date']
                    list_of_sku = dist_of_purchase_orders[pid]['sku']
                    list_of_sku = ';'.join(str(e) for e in list_of_sku)
                    list_of_qty = dist_of_purchase_orders[pid]['qty']
                    list_of_in_stock = ["True"] * len(list_of_qty)
                    list_of_in_stock = ';'.join(str(e) for e in list_of_in_stock)

                    list_of_qty = ';'.join(str(e) for e in list_of_qty)
                    if ("part_no" in dist_of_purchase_orders[pid]):
                        list_of_part_number = dist_of_purchase_orders[pid]['part_no']
                        list_of_part_number = 'FD_PART'.join(str(e) for e in list_of_part_number)
                    else:
                        list_of_part_number = 'NA'

                    # purchase_order = purchaseorder(purchase_orderid=purchase_id)

                    try:
                        # Trying to look for already inserted
                        purchase_order = purchaseorder.objects.get(purchase_orderid=purchase_id)
                        print("Found!")
                    except:
                        print("Not Found! Inserting")
                        purchase_order = purchaseorder(purchase_orderid=purchase_id,
                                                       supplier_name=Supplier_Details.objects.get(
                                                           supplier_name=supplier_name),
                                                       created_date=date,
                                                       tracking_id=tracking_number,
                                                       courier=courier, alias=purchase_id, legacy_purchase_id=True)
                        purchase_order.save()

                    try:
                        # Trying to look for already inserted
                        purchase_order_details = purchaseorder_details.objects.get(purchase_orderid=str(purchase_id))
                        print("Found!")
                    except:
                        print("Not Found! Inserting")
                        purchase_order_details = purchaseorder_details(
                            purchase_orderid=purchaseorder.objects.get(purchase_orderid=str(purchase_id)),
                            sku=list_of_sku,
                            qty=list_of_qty,
                            instock=list_of_in_stock,
                            part_number=list_of_part_number)

                        purchase_order_details.save()

            return HttpResponse("<h1>Post Received</h1>")
        else:
            return HttpResponse("<h1>Invalid Post</h1>")


    else:
        return HttpResponse("<h1>Invalid Post</h1>")
