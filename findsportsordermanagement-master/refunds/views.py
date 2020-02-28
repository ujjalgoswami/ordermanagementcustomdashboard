from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import date
# Create your views here.
from home.views import refunded, to_be_refunded, dispatched
from purchaseorder.models import orderline, purchaseorder, orderid_purchaseorderid

@login_required
def index(request):
    dict_orderlineid=purchaseorderoutofstockrefunds()

    return render(request, 'refunds/refunds.html', {"refunds":True, "dict_orderlineid":dict_orderlineid})


# This function shows a list of orders which are to be refunded due to purchase order out of stock. Things considered are-
# showing orders where stock is not equal to quantity
# excluding orders from already dispatched
# exluding orders from already refunded
# exluding orders from pending refund


def productavailableinstore(request):
    if request.method == 'POST':
        dict_of_post_items = request.POST.items()

        orderlineid = request.POST.get("orderlineid")
        if ('available_in_store' in request.POST):
            orderline.objects.filter(order_line_id=orderlineid).update(available_in_store=True,refund_resolved=True)
        elif('resolved' in request.POST):
            orderline.objects.filter(order_line_id=orderlineid).update(refund_resolved=True)

    return redirect('/refunds')

def purchaseorderoutofstockrefunds():
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")
    year = int(today_date.split("-")[0])
    month = int(today_date.split("-")[1])
    day = int(today_date.split("-")[2])
    today_date = date(year, month, day)

    orders = orderline.objects.filter(qty__isnull=False,refund_resolved=False).exclude(instock=F("qty"))

    list_of_order_line_ids = []
    for temp in orders:
        list_of_order_line_ids.append(temp.order_line_id)

    order_id_purchaseorders = orderid_purchaseorderid.objects.filter(order_line_id__in=list_of_order_line_ids)

    dict_orderline_oderid = {}
    for temp in order_id_purchaseorders:
        dict_orderline_oderid[temp.order_line_id] = temp.order_id

    # tuple_of_dispatched_orderids = dispatched()[0]
    # list_of_orderids3 = []
    # for index in range(0, len(tuple_of_dispatched_orderids)):
    #     list_of_orderids3.append(tuple_of_dispatched_orderids[index][0])

    tuple_of_refunded_orderids = refunded()[0]
    list_of_orderids = []
    for index in range(0, len(tuple_of_refunded_orderids)):
        list_of_orderids.append(tuple_of_refunded_orderids[index][0])

    tuple_of_toberefunded_orderids = to_be_refunded(today_date)[0]

    list_of_orderids2 = []
    for index in range(0, len(tuple_of_toberefunded_orderids)):
        list_of_orderids2.append(tuple_of_toberefunded_orderids[index][0])

    list_of_purchase_order_ids = []
    dict_orderlineid = {}
    for temp in orders:
        order_id = dict_orderline_oderid[temp.order_line_id]
        # if not ((order_id in list_of_orderids) or (order_id in list_of_orderids2) or (order_id in list_of_orderids3)):
        if not ((order_id in list_of_orderids) or (order_id in list_of_orderids2) ):
            tempdict = {}
            tempdict['orderid'] = order_id
            tempdict['order_line_id'] = temp.order_line_id
            tempdict['sku'] = temp.sku
            tempdict['qty'] = temp.qty
            tempdict['instock'] = temp.instock
            tempdict['purchase_orderid_id'] = temp.purchase_orderid_id
            list_of_purchase_order_ids.append(temp.purchase_orderid_id)
            dict_orderlineid[temp.order_line_id] = tempdict

    p_order = purchaseorder.objects.filter(purchase_orderid__in=list_of_purchase_order_ids)
    dict_purchase_order = {}
    for porder in p_order:
        dict_purchase_order[porder.purchase_orderid] = {"alias": porder.alias, "submitted_date": porder.submitted_date}

    for temp2 in dict_orderlineid:
        dict_orderlineid[temp2]['alias'] = dict_purchase_order[dict_orderlineid[temp2]['purchase_orderid_id']]['alias']
        dict_orderlineid[temp2]['submitted_date'] = dict_purchase_order[dict_orderlineid[temp2]['purchase_orderid_id']][
            'submitted_date']

    return dict_orderlineid
