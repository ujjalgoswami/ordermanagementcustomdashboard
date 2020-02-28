from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from io import StringIO
from django.contrib import messages
from datetime import date
import numpy as np
from io import BytesIO
from django.db.models import Q
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from weasyprint import HTML
import requests
from xlsxwriter import Workbook
from django.http import HttpResponse

import datetime
from findsportsordermanagement.cron import insert_data, insert_backorders
from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response, sendemail
from suppliers.models import Supplier_Details, SupplierNew
from purchaseorder.models import orderid_purchaseorderid, purchaseorder, purchaseorder_details, orderline, \
    sub_purchaseorder

today = date.today()
today_date = today.strftime("%Y-%m-%d")
year = int(today_date.split("-")[0])
month = int(today_date.split("-")[1])
day = int(today_date.split("-")[2])
today_date = date(year, month, day)


def temp_function(p_id):
    try:
        p_order = purchaseorder.objects.get(purchase_orderid=str(p_id))
        p_order_details = purchaseorder_details.objects.get(purchase_orderid=str(p_id))

        pid_not_found = False
    except:
        pid_not_found = True

    if (pid_not_found == False):

        # This is for getting if the purchase order is eligible for submitting or not!
        supplier_name = getattr(p_order.supplier_name, "supplier_name")

        supplier_details = Supplier_Details.objects.get(supplier_name=supplier_name)
        supplier_short_code = supplier_details.short_code

        list_of_orderlineids = p_order_details.order_line_id.split(";")

        list_of_skus = p_order_details.sku.split(";")
        list_of_qty = p_order_details.qty.split(";")
        list_of_part_number = p_order_details.part_number.split("FD_PART")
        list_of_instock = p_order_details.instock.split(";")

        if (len(list_of_orderlineids) > 0 and list_of_orderlineids[0] != ""):

            dict_order_line_id_sku_qty_part_number_instock = {}

            for index in range(0, len(list_of_orderlineids)):
                order_line_id = list_of_orderlineids[index]
                sku = list_of_skus[index]
                qty = list_of_qty[index]
                part_no = list_of_part_number[index]
                stock = list_of_instock[index]

                temp_dict = {}
                temp_dict['order_line_id'] = order_line_id
                temp_dict['sku'] = sku
                temp_dict['qty'] = qty
                temp_dict['part_no'] = part_no
                temp_dict['stock'] = stock
                dict_order_line_id_sku_qty_part_number_instock[list_of_orderlineids[index]] = temp_dict

            dict_supplier_details = get_supplier_details(list_of_orderlineids, supplier_short_code)

            for order_l_id in dict_supplier_details['dict_of_order_line_id_orderid_sku']:
                dict_supplier_details['dict_of_order_line_id_orderid_sku'][order_l_id]['ORDERLINEID'] = order_l_id
                dict_supplier_details['dict_of_order_line_id_orderid_sku'][order_l_id]['QTY'] = \
                    dict_order_line_id_sku_qty_part_number_instock[order_l_id]['qty']
                dict_supplier_details['dict_of_order_line_id_orderid_sku'][order_l_id]['PARTNO'] = \
                    dict_order_line_id_sku_qty_part_number_instock[order_l_id]['part_no']
                dict_supplier_details['dict_of_order_line_id_orderid_sku'][order_l_id]['STOCK'] = \
                    dict_order_line_id_sku_qty_part_number_instock[order_l_id]['stock']

            return dict_supplier_details['dict_of_order_line_id_orderid_sku']
        else:
            return ""


def temp_cron_new_table_orderline_id():
    list_of_purchase_id = []
    p_order_main = purchaseorder.objects.all()
    for temp in p_order_main:
        list_of_purchase_id.append(temp.purchase_orderid)

    batch = []
    for index in range(0, len(list_of_purchase_id)):

        dict_order_lineid_sku_qty_part_number_stock_pid = temp_function(list_of_purchase_id[index])

        if (len(dict_order_lineid_sku_qty_part_number_stock_pid) > 0):
            for temp3 in dict_order_lineid_sku_qty_part_number_stock_pid:

                orderlineid = dict_order_lineid_sku_qty_part_number_stock_pid[temp3]['ORDERLINEID']
                sku = dict_order_lineid_sku_qty_part_number_stock_pid[temp3]['SKU']
                qty = dict_order_lineid_sku_qty_part_number_stock_pid[temp3]['QTY']
                part_number = dict_order_lineid_sku_qty_part_number_stock_pid[temp3]['PARTNO']
                stock = dict_order_lineid_sku_qty_part_number_stock_pid[temp3]['STOCK']
                p_id = list_of_purchase_id[index]

                try:
                    # trying to look for already inserted
                    order = orderline.objects.get(order_line_id=orderlineid)
                except:
                    query = orderline(order_line_id=orderlineid, sku=sku, part_number=part_number, qty=qty,
                                      instock=stock,
                                      purchase_orderid=purchaseorder.objects.get(purchase_orderid=str(p_id)))

                    batch.append(query)

    batch_size = 50
    orderline.objects.bulk_create(batch, batch_size)


def get_purchase_order_id_details(p_id):
    try:
        p_order = purchaseorder.objects.get(purchase_orderid=str(p_id))

        pid_not_found = False
    except:
        pid_not_found = True

    if (p_order.legacy_purchase_id):
        p_order_details = purchaseorder_details.objects.get(purchase_orderid=str(p_id))

    if (pid_not_found == False):

        # This is for getting if the purchase order is eligible for submitting or not!
        supplier_name = getattr(p_order.supplier_name, "supplier_name")
        supplier_details = Supplier_Details.objects.get(supplier_name=supplier_name)
        supplier_short_code = supplier_details.short_code

        list_of_skus = []
        if not (p_order.legacy_purchase_id):
            ord_line = orderline.objects.filter(purchase_orderid=str(p_id),dropship=False)
            for single_order_line in ord_line:
                list_of_skus.append(single_order_line.sku)

        else:
            # legacy purchase order
            list_of_skus = p_order_details.sku.split(";")

        temp_dict = get_supplier_details(None, supplier_short_code, list_of_skus)

        eligible = temp_dict['eligible']
        msg = temp_dict['msg']
        costprice = temp_dict['costprice']

        list_of_qty = []
        list_of_part_number = []
        list_of_instock = []
        list_of_order_line_id = []
        list_of_isDropShip = []
        list_of_isReorder = []

        if not (p_order.legacy_purchase_id):

            ord_line = orderline.objects.filter(purchase_orderid=str(p_id))

            for single_order_line in ord_line:
                list_of_qty.append(single_order_line.qty)
                list_of_part_number.append(single_order_line.part_number)
                list_of_instock.append(single_order_line.instock)
                list_of_order_line_id.append(single_order_line.order_line_id)
                list_of_isDropShip.append(single_order_line.dropship)
                list_of_isReorder.append(single_order_line.reorder)
        else:
            # If Legacy system
            list_of_qty = p_order_details.qty.split(";")
            list_of_part_number = p_order_details.part_number.split("FD_PART")
            list_of_instock = p_order_details.instock.split(";")

        temp_response = api_product_response({"SKU": list_of_skus},
                                             ["Brand", "Name"])
        temp_list = temp_response['Item']
        temp_dict = {}
        for product in temp_list:
            brand = product['Brand']
            name = product['Name']
            sku = product['SKU']
            temp_dict[sku] = {'Name': name, 'Brand': brand}

        dict_sku_part_number = {}
        for index in range(0, len(list_of_order_line_id)):
            dict_sku_part_number[list_of_order_line_id[index]] = {"sku": list_of_skus[index],
                                                                  "orderlineid": list_of_order_line_id[index],
                                                                  "qty": list_of_qty[index],
                                                                  "partnumber": list_of_part_number[index],
                                                                  "stock": str(list_of_instock[index]).replace("True",
                                                                                                               str(
                                                                                                                   list_of_qty[
                                                                                                                       index])).replace(
                                                                      "False", "0"),
                                                                  "dropship": list_of_isDropShip[index],"reorder":list_of_isReorder[index]}

        if (True in list_of_isDropShip):
            # Subpurchase orders exist
            viewsubpurchaseorders = True
        else:
            viewsubpurchaseorders = False

        purchase_order_id = p_id
        purchase_order_created_date = p_order.created_date
        purchase_order_suppliername = p_order.supplier_name_id
        purchase_order_trackingid = p_order.tracking_id
        purchase_order_courier = p_order.courier
        purchase_order_submitted = p_order.submitted
        purchase_order_submitted_date = p_order.submitted_date
        purchase_order_submitted_alias = p_order.alias
        internal_notes=p_order.internal_notes
        received_date=p_order.received_date

        if (len(purchase_order_trackingid) > 0 and purchase_order_trackingid != "NA"):
            tracking = True
        else:
            tracking = False

        order_ids_purchaseorderids = orderid_purchaseorderid.objects.filter(purchase_orderid=str(p_id))
        list_of_order_ids = []
        for temp in order_ids_purchaseorderids:
            list_of_order_ids.append(temp.order_id)

        if (len(list_of_order_ids) > 0):
            show_order_ids = True
        else:
            show_order_ids = False

        return [list_of_skus, temp_dict, list_of_qty, list_of_part_number, purchase_order_id,
                purchase_order_submitted_alias, list_of_instock, purchase_order_trackingid, purchase_order_courier,
                tracking, purchase_order_suppliername, purchase_order_created_date, dict_sku_part_number,
                list_of_order_ids, show_order_ids, purchase_order_submitted, purchase_order_submitted_date, eligible,
                msg, costprice, viewsubpurchaseorders,internal_notes,received_date]

    else:
        # Invalid PID
        return redirect("/")


def viewpurchaseorder(request, p_id, stock_confirm=False):
    warehouse = request.GET.get('warehouse')
    if (warehouse == None):
        warehouse = False
    else:
        warehouse = bool(warehouse)

    master_list = get_purchase_order_id_details(p_id)
    list_of_skus = master_list[0]
    temp_dict = master_list[1]
    list_of_qty = master_list[2]
    list_of_part_number = master_list[3]
    purchase_order_id = master_list[4]
    purchase_order_submitted_alias = master_list[5]
    list_of_instock = master_list[6]
    purchase_order_trackingid = master_list[7]
    purchase_order_courier = master_list[8]
    tracking = master_list[9]
    purchase_order_suppliername = master_list[10]
    purchase_order_created_date = master_list[11]
    dict_sku_part_number = master_list[12]
    list_of_order_ids = master_list[13]
    show_order_ids = master_list[14]
    purchase_order_submitted = master_list[15]
    purchase_order_submitted_date = master_list[16]
    eligible = master_list[17]
    msg = master_list[18]
    costprice = master_list[19]
    viewsubpurchaseorders = master_list[20]
    internal_notes=master_list[21]
    received_date=master_list[22]

    # For File download
    file_type_to_download = request.GET.get('download')
    if (file_type_to_download):
        if (file_type_to_download == 'downloadpurchaseorder'):
            return create_excel(list_of_skus, temp_dict, list_of_qty, list_of_part_number, purchase_order_id,
                                purchase_order_submitted_alias, list_of_instock)

    courier_link = get_trackinglink(purchase_order_trackingid, purchase_order_courier)

    if not (stock_confirm):
        return render(request, 'purchaseorder/purchaseorder.html',
                      {"tracking": tracking,"internal_notes":internal_notes,"received_date":received_date,
                       "purchase_order_details": True, "purchase_order_courier": purchase_order_courier,
                       "purchase_order_trackingid": purchase_order_trackingid,
                       "purchase_order_suppliername": purchase_order_suppliername,
                       "purchase_order_id": purchase_order_id,
                       "purchase_order_created_date": purchase_order_created_date, "nopurchaseorders": True,
                       "purchaseorder": True, "dict_sku_part_number": dict_sku_part_number,
                       "list_of_order_ids": list(set(list_of_order_ids)), "show_order_ids": show_order_ids,
                       "purchase_order_submitted": purchase_order_submitted,
                       "purchase_order_submitted_date": purchase_order_submitted_date,
                       "purchase_order_submitted_alias": purchase_order_submitted_alias,
                       "eligible": eligible, "msg": msg, "costprice": costprice, "courier_link": courier_link,
                       "viewsubpurchaseorders": viewsubpurchaseorders
                       })
    else:
        # Stock confirm True

        list_of_order_ids = list(set(list_of_order_ids))
        orderlinedetails = orderline.objects.filter(purchase_orderid=str(p_id))
        dict_order_line_id_sku_partno_qty_instock = {}
        for temp in orderlinedetails:
            temp_dict = {}
            temp_dict['order_line_id'] = temp.order_line_id
            temp_dict['sku'] = temp.sku
            temp_dict['part_number'] = temp.part_number
            temp_dict['qty'] = temp.qty
            temp_dict['instock'] = temp.instock
            dict_order_line_id_sku_partno_qty_instock[temp.order_line_id] = temp_dict

        # check if request is coming from warehouse
        if not (warehouse):

            return render(request, 'purchaseorder/purchaseorderstockconfirm.html',
                          {"tracking": tracking,
                           "purchase_order_details": True, "purchase_order_courier": purchase_order_courier,
                           "purchase_order_trackingid": purchase_order_trackingid,
                           "purchase_order_suppliername": purchase_order_suppliername,
                           "purchase_order_id": purchase_order_id,
                           "purchase_order_created_date": purchase_order_created_date, "nopurchaseorders": True,
                           "purchaseorder": True,
                           "dict_order_line_id_sku_partno_qty_instock": dict_order_line_id_sku_partno_qty_instock,
                           "purchase_order_submitted": purchase_order_submitted,
                           "purchase_order_submitted_date": purchase_order_submitted_date,
                           "purchase_order_submitted_alias": purchase_order_submitted_alias,
                           "costprice": costprice, "courier_link": courier_link
                           })
        else:

            return render(request, 'warehouse/purchaseordersreceivedstockconfirm.html',
                          {"tracking": tracking,
                           "purchase_order_details": True, "purchase_order_courier": purchase_order_courier,
                           "purchase_order_trackingid": purchase_order_trackingid,
                           "purchase_order_suppliername": purchase_order_suppliername,
                           "purchase_order_id": purchase_order_id,
                           "purchase_order_created_date": purchase_order_created_date, "nopurchaseorders": True,
                           "purchaseorder": True,
                           "dict_order_line_id_sku_partno_qty_instock": dict_order_line_id_sku_partno_qty_instock,
                           "purchase_order_submitted": purchase_order_submitted,
                           "purchase_order_submitted_date": purchase_order_submitted_date,
                           "purchase_order_submitted_alias": purchase_order_submitted_alias,
                           "costprice": costprice, "courier_link": courier_link
                           })


def viewallpurchaseorders(request, date_created=None, template=None, supplier_name=None):
    if not (supplier_name == None):
        # Handling requests coming from warehouse homepage where the user clicks on a suppliername to get the list of purchase orders
        p_orders = purchaseorder.objects.filter(supplier_name=supplier_name, legacy_purchase_id=False, received=False,
                                                submitted=True)
    else:
        p_orders = purchaseorder.objects.all()

    dict_porder = {}

    list_of_created_dates = []

    for porder in p_orders:
        list_of_created_dates.append(porder.created_date)
        dict_porder[porder.alias] = {"purchase_order_id": porder.purchase_orderid, "Supplier": porder.supplier_name_id,
                                     "CreatedDate": porder.created_date,
                                     "trackingid": porder.tracking_id, "courier": porder.courier,
                                     "submitted": porder.submitted,
                                     "SubmittedDate": porder.submitted_date
                                     }

    unique_list_of_created_dates = list(set(list_of_created_dates))

    if (date_created == None and supplier_name == None):
        return unique_list_of_created_dates
    elif not (supplier_name == None):
        # filter content based on suppliername
        supplier_dict = {}
        for temp in dict_porder:

            if (dict_porder[temp]['Supplier'] == supplier_name):
                supplier_dict[temp] = dict_porder[temp]

        if (template == None):

            # sorting the list based on submitted or not
            List_of_dated_dict = [(purchase_id_alias, supplier_dict[purchase_id_alias]['purchase_order_id'],
                                   supplier_dict[purchase_id_alias]['Supplier'],
                                   supplier_dict[purchase_id_alias]['SubmittedDate'],
                                   supplier_dict[purchase_id_alias]['trackingid'],
                                   supplier_dict[purchase_id_alias]['courier'],
                                   supplier_dict[purchase_id_alias]['submitted'])
                                  for purchase_id_alias in supplier_dict.keys()]
            list1 = list(map(list, zip(*List_of_dated_dict)))
            if (len(list1) > 0):
                List_of_dated_dict = zip(list1[0], list1[1], list1[2], list1[3], list1[4], list1[5], list1[6])
                List_of_dated_dict = list(List_of_dated_dict)
            List_of_dated_dict = sorted(List_of_dated_dict, key=lambda x: x[3], reverse=False)

            return render(request, 'warehouse/purchaseorders.html',
                          {"number_of_purchase_orders": len(supplier_dict),
                           "List_of_dated_dict": List_of_dated_dict, "supplier_name": supplier_name})
    else:
        # filter content based on date
        dated_dict = {}
        for temp in dict_porder:

            if (dict_porder[temp]['CreatedDate'] == date_created.date()):
                dated_dict[temp] = dict_porder[temp]

        if (template == None):

            # sorting the list based on submitted or not
            List_of_dated_dict = [(purchase_id_alias, dated_dict[purchase_id_alias]['purchase_order_id'],
                                   dated_dict[purchase_id_alias]['Supplier'],
                                   dated_dict[purchase_id_alias]['CreatedDate'],
                                   dated_dict[purchase_id_alias]['trackingid'],
                                   dated_dict[purchase_id_alias]['courier'], dated_dict[purchase_id_alias]['submitted'])
                                  for purchase_id_alias in dated_dict.keys()]
            list1 = list(map(list, zip(*List_of_dated_dict)))
            if (len(list1) > 0):
                List_of_dated_dict = zip(list1[0], list1[1], list1[2], list1[3], list1[4], list1[5], list1[6])
                List_of_dated_dict = list(List_of_dated_dict)
            List_of_dated_dict = sorted(List_of_dated_dict, key=lambda x: x[6], reverse=False)

            return render(request, 'purchaseorder/purchaseorders.html',
                          {"number_of_purchase_orders": len(dated_dict),
                           "List_of_dated_dict": List_of_dated_dict, "created_on_date": date_created.date()})
        else:
            return render(request, template,
                          {"number_of_purchase_orders": len(dated_dict),
                           "dict_of_purchase_orders": dated_dict, "created_on_date": date_created.date()})


def generate_synced_new_backorder_order_line_ids():
    # Fetching all orderids which have a status of New Backorder
    temp_response = api_order_response({"OrderStatus": "New Backorder"},
                                       ["OrderID", "OrderLine", "OrderLine.ProductName"])
    response = temp_response['Order']

    list_of_newbackorder_order_line_ids = []

    dict_orderlineid_sku_qty_productname = {}
    for order in response:
        temp_list_of_order_lines = order['OrderLine']
        for singleorderline in temp_list_of_order_lines:
            order_line_id = singleorderline['OrderLineID']
            temp_dict = {}
            temp_dict['SKU'] = singleorderline['SKU']
            temp_dict['ProductName'] = singleorderline['ProductName']
            temp_dict['Quantity'] = singleorderline['Quantity']

            dict_orderlineid_sku_qty_productname[order_line_id] = temp_dict

            list_of_newbackorder_order_line_ids.append(order_line_id)

    orders = SupplierNew.objects.filter(order_line_id__in=list_of_newbackorder_order_line_ids,
                                        purchase_order_generated=False)

    result_ids = [result.order_line_id for result in orders]

    list_of_order_line_ids_not_found = [None if order_id in result_ids else order_id for order_id in
                                        list_of_newbackorder_order_line_ids]

    # These order ids will be synced in the next cron run
    list_of_order_line_ids_not_found = [x for x in list_of_order_line_ids_not_found if x is not None]

    list_of_synced_newbackorder_order_order_line_ids = [x for x in list_of_newbackorder_order_line_ids if
                                                        x not in list_of_order_line_ids_not_found]

    return [list_of_synced_newbackorder_order_order_line_ids, dict_orderlineid_sku_qty_productname]


def get_unique_suppliers(list_of_synced_newbackorder_order_line_ids):
    orders = SupplierNew.objects.filter(order_line_id__in=list_of_synced_newbackorder_order_line_ids)
    list_of_suppliers = []
    for temp in orders:
        list_of_suppliers.append(temp.primarysupplier)

    unique_list_of_suppliers = list(set(list_of_suppliers))

    unique_list_of_suppliers = list(filter(('FIND_Imports').__ne__, unique_list_of_suppliers))
    unique_list_of_suppliers = list(filter(('Mizu').__ne__, unique_list_of_suppliers))


    return unique_list_of_suppliers


def get_supplier_details(list_of_synced_newbackorder_order_line_ids, supplier, optional_list_sku=None):
    dict_of_order_line_id_orderid_sku = {}
    final_sku_list = []

    if not (list_of_synced_newbackorder_order_line_ids == None):
        orders = SupplierNew.objects.filter(order_line_id__in=list_of_synced_newbackorder_order_line_ids,
                                            primarysupplier=supplier)
        for temp in orders:
            order_line_id = temp.order_line_id
            order_id = temp.order_id
            sku = temp.sku
            supplier = temp.primarysupplier
            final_sku_list.append(sku)
            temp_dict = {}
            temp_dict['SKU'] = sku
            temp_dict['order_id'] = order_id

            dict_of_order_line_id_orderid_sku[order_line_id] = temp_dict
    else:
        if not (optional_list_sku == None):
            final_sku_list = optional_list_sku

    cost_price = api_product_response({"SKU": final_sku_list}, "Misc27")

    temp_list = cost_price['Item']
    costprice = 0
    for prod in temp_list:
        try:
            costprice = costprice + float(prod['Misc27'])
        except:
            costprice=costprice+0

    supplier_details = Supplier_Details.objects.get(short_code=supplier)

    minimum_order = supplier_details.minimum_order
    email = supplier_details.supplier_email

    if (costprice >= float(minimum_order)):
        msg = "Supplier eligible for purchase order"
        eligible = True
    else:
        msg = "$" + str(round(float(minimum_order) - costprice, 1)) + " more required to be eligible"
        eligible = False

    temp_dict = {}
    temp_dict['eligible'] = eligible
    temp_dict['msg'] = msg
    temp_dict['costprice'] = round(costprice, 1)
    temp_dict['final_sku_list'] = final_sku_list
    temp_dict['dict_of_order_line_id_orderid_sku'] = dict_of_order_line_id_orderid_sku

    return temp_dict


def createNewPurchaseOrder(request):
    # For the page where all suppliers are visible

    list_of_synced_newbackorder_order_line_ids = generate_synced_new_backorder_order_line_ids()[0]

    # Getting a list of unique suppliers (This contains orders with no supplier as well)
    unique_list_of_suppliers = get_unique_suppliers(list_of_synced_newbackorder_order_line_ids)

    # Removing orders which dont have any supplier name
    unique_list_of_suppliers = ["No_Supplier" if x == '' else x for x in unique_list_of_suppliers]
    unique_list_of_suppliers = list(filter(("No_Supplier").__ne__, unique_list_of_suppliers))

    supplier = request.GET.get('supplier')
    if not (supplier is None):

        temp_dict = get_supplier_details(list_of_synced_newbackorder_order_line_ids, supplier)

        return render(request, 'purchaseorder/purchaseorders.html',
                      {"generate_purchase_order": True, "SupplierSelected": True,
                       "eligible": temp_dict['eligible'], "msg": temp_dict['msg'], "costprice": temp_dict['costprice'],
                       "supplier": supplier,
                       "final_sku_list": temp_dict['final_sku_list'],
                       "dict_of_sku_order_id": temp_dict['dict_of_order_line_id_orderid_sku'],
                       'unique_list_of_suppliers': unique_list_of_suppliers})
    else:
        # No supplier was selected , Show list of suppliers
        if (len(unique_list_of_suppliers) > 0):
            nosuppliersfound = False
        else:
            nosuppliersfound = True

        return render(request, 'purchaseorder/purchaseorders.html',
                      {"SupplierSelected": False, "generate_purchase_order": True,
                       'unique_list_of_suppliers': unique_list_of_suppliers, "nosuppliersfound": nosuppliersfound})


def shownewpurchaseorderdetails(request, supplier):
    list_of_synced_newbackorder_order_ids = generate_synced_new_backorder_order_line_ids()[0]

    dict_orderlineid_sku_qty_productname = generate_synced_new_backorder_order_line_ids()[1]

    temp_dict = get_supplier_details(list_of_synced_newbackorder_order_ids, supplier)

    dict_of_order_line_id_orderid_sku = temp_dict['dict_of_order_line_id_orderid_sku']

    # Getting the list of unique skus to retrieve their partnumbers
    list_of_unique_skus = []
    for orderlineid in dict_of_order_line_id_orderid_sku:
        sku = dict_of_order_line_id_orderid_sku[orderlineid]['SKU']
        list_of_unique_skus.append(sku)

    list_of_unique_skus = list(set(list_of_unique_skus))

    List_of_dist_sku_partnumbers = api_product_response({"SKU": list_of_unique_skus}, 'Misc10', None)['Item']
    dict_sku_part_number = {}
    for sku_partnumber_dict in List_of_dist_sku_partnumbers:
        dict_sku_part_number[sku_partnumber_dict['SKU']] = sku_partnumber_dict['Misc10']

    cost_price = temp_dict['costprice']

    dict_sku_order_id_qty_name = {}

    for order_line_id in dict_of_order_line_id_orderid_sku:
        sku = dict_of_order_line_id_orderid_sku[order_line_id]['SKU']
        order_id = dict_of_order_line_id_orderid_sku[order_line_id]['order_id']
        temp_dict = {}
        temp_dict['sku'] = sku
        temp_dict['order_id'] = order_id
        temp_dict['qty'] = dict_orderlineid_sku_qty_productname[order_line_id]['Quantity']
        temp_dict['name'] = dict_orderlineid_sku_qty_productname[order_line_id]['ProductName']
        temp_dict['order_line_id'] = order_line_id
        try:
            part_number = dict_sku_part_number[sku]
        except:
            part_number = "nan"

        if (str(part_number) == "nan" or part_number == None):
            temp_dict['part_number'] = ''
        else:
            temp_dict['part_number'] = part_number

        dict_sku_order_id_qty_name[(sku, order_id)] = temp_dict

    # Alerting user against creating a new purchase order if a previous purchase order for the supplier is unsubmitted

    sup_details = Supplier_Details.objects.get(short_code=supplier)
    sup_name = sup_details.supplier_name
    list_of_submit_pending = viewPendingSubmitCreatedPurchaseOrders()
    dict_supplier_name_purchaseorderid = {}
    if (len(list_of_submit_pending) > 0):

        for order in list_of_submit_pending:
            temp_dict = {}
            temp_dict['suppliername'] = order[4]
            temp_dict['pid'] = order[3]
            temp_dict['alias'] = order[0]

            dict_supplier_name_purchaseorderid[order[4]] = temp_dict

    if (sup_name in dict_supplier_name_purchaseorderid):
        supplier_message = "Attention! An unsubmitted purchase order " + dict_supplier_name_purchaseorderid[sup_name][
            'pid'] + " with alias " + dict_supplier_name_purchaseorderid[sup_name][
                               'alias'] + " already exists for the supplier " + sup_name + ". The products of this order will be added to the previous purchase order. If you still wish to create a brand new purchase order, please submit the previous purchase order or remove the pre-filled purchase order id from the textbox above the submit button."
        purchaseorder_override = dict_supplier_name_purchaseorderid[sup_name]['pid']
    else:
        purchaseorder_override = ""
        if (sup_details.website_order_placement):
            supplier_message = "Note: This Supplier has been marked for Online ordering. After placing the orders on the suppliers website, please mark the purchase order as submitted and confirm the stock."
        else:
            supplier_message = "Note: This Supplier has been marked for ordering via email. After sending the purchase order to the supplier, please mark the purchase order as submitted and confirm the stock from the supplier."

    return render(request, 'purchaseorder/newpurchaseorder.html',
                  {"dict_sku_order_id_qty": dict_sku_order_id_qty_name,
                   "supplier": supplier, "today": datetime.date.today(), "costprice": cost_price,
                   "supplier_message": supplier_message, "purchaseorder_override": purchaseorder_override})


def processcronnewbackorder(request):
    if request.method == 'POST':

        insert_backorders()
        return redirect('/purchaseorder/?newPurchaseOrder=True')
    else:
        return redirect('/')


def html_to_pdf_view(request, p_id):
    master_list = get_purchase_order_id_details(p_id)
    list_of_skus = master_list[0]
    temp_dict = master_list[1]
    list_of_qty = master_list[2]
    list_of_part_number = master_list[3]
    purchase_order_id = master_list[4]
    purchase_order_submitted_alias = master_list[5]
    list_of_instock = master_list[6]
    purchase_order_trackingid = master_list[7]
    purchase_order_courier = master_list[8]
    tracking = master_list[9]
    purchase_order_suppliername = master_list[10]
    purchase_order_created_date = master_list[11]
    dict_sku_part_number = master_list[12]
    list_of_order_ids = master_list[13]
    show_order_ids = master_list[14]
    purchase_order_submitted = master_list[15]
    purchase_order_submitted_date = master_list[16]
    eligible = master_list[17]
    msg = master_list[18]
    costprice = master_list[19]
    viewsubpurchaseorders = master_list[20]

    totalqty = sum(list_of_instock)
    sample_rows = []
    for orderlineid in dict_sku_part_number:
        orderline_id = orderlineid
        sku = dict_sku_part_number[orderlineid]['sku']
        qty = dict_sku_part_number[orderlineid]['qty']
        partnumber = dict_sku_part_number[orderlineid]['partnumber']
        stock = dict_sku_part_number[orderlineid]['stock']
        name = temp_dict[sku]['Name']

        sample_rows.append(

        "<tr><td>" + str(orderline_id) + "</td><td>" + str(sku) + "</td><td>" + str(
            name) + "</td><td>" + str(stock) + "</td><td>" + str(
            partnumber) + "</td>")

    html_string = render_to_string('pdf/pdf_template.html', {'sample_rows': sample_rows, 'totalqty': totalqty,
                                                             "purchase_order_id": purchase_order_id,
                                                             "purchase_order_submitted_alias": purchase_order_submitted_alias,
                                                             "purchase_order_suppliername": purchase_order_suppliername,
                                                             "purchase_order_submitted_date": purchase_order_submitted_date})

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/mypdf.pdf');

    fs = FileSystemStorage('/tmp')
    filename = str(purchase_order_submitted_alias) + ".pdf"
    with fs.open('mypdf.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=' + filename + ''
        return response

    return response


def purchaseorderstockconfirm(request):
    if request.method == 'POST':
        pid = request.POST.get("pid")
        warehouse = request.POST.get("warehouse")
        if not (warehouse == None):
            warehouse = True
        else:
            warehouse = False

        if ('save' in request.POST):

            p_order = purchaseorder.objects.get(purchase_orderid=pid)
            p_order.stock_confirmed = True
            p_order.tracking_id='RECEIVED'
            p_order.save(update_fields=['stock_confirmed'])

            if (warehouse):
                p_order.received = True
                p_order.received_date = datetime.datetime.now().date()
                p_order.save(update_fields=['received'])
                p_order.save(update_fields=['received_date'])
                p_order.save(update_fields=['tracking_id'])
                return redirect('/warehouse/')
            else:
                return redirect('/purchaseorder/')

        elif ('update' in request.POST):

            dict_order_line_id_stock = {}
            dict_of_post_items = request.POST.items()
            for index, item in enumerate(dict_of_post_items):
                tupple = item
                key = tupple[0]
                value = tupple[1]
                if not ("csrfmiddlewaretoken" == key):
                    if ("instock" in key):
                        orderlineid = key.split(":")[0]
                        stock = value
                        dict_order_line_id_stock[orderlineid] = stock

            with transaction.atomic():
                for orderlineid in dict_order_line_id_stock:
                    orderline.objects.filter(order_line_id=orderlineid).update(
                        instock=dict_order_line_id_stock[orderlineid])

            p_order = purchaseorder.objects.get(purchase_orderid=pid)
            p_order.stock_confirmed = True
            p_order.tracking_id = 'RECEIVED'
            p_order.save(update_fields=['stock_confirmed'])

            if (warehouse):
                p_order.received = True
                p_order.received_date = datetime.datetime.now().date()
                p_order.save(update_fields=['received'])
                p_order.save(update_fields=['received_date'])
                p_order.save(update_fields=['tracking_id'])
                return redirect('/warehouse/')
            else:
                return redirect('/purchaseorder/')
    else:
        p_id = request.GET.get('pid')
        is_warehouse = request.GET.get('warehouse')

        file_type_to_download = request.GET.get('download')

        if (file_type_to_download):
            if (file_type_to_download == 'downloadchecklist'):
                return html_to_pdf_view(request, p_id)

        if (is_warehouse == True and p_id != None):
            return viewpurchaseorder(request, p_id, True)
        elif not (p_id is None):
            # When a purchase id exists in the header
            return viewpurchaseorder(request, p_id, True)
        else:
            return redirect('/')


def get_trackinglink(trackingid, courier):
    link = ""
    courier = courier.lower().replace(" ", "")
    if (courier == 'tnt'):
        link = "https://www.tnt.com/express/en_au/site/shipping-tools/tracking.html?navigation=1&searchType=CON&cons=" + str(
            trackingid)
    elif (courier == 'auspost'):
        link = "https://auspost.com.au/mypost/track/#/details/" + str(trackingid)
    elif (courier == 'victasfreight'):
        link = "https://portal.vtfe.com.au/Track/VTFE/" + str(trackingid)
    elif (courier == 'dfe'):
        link = 'https://www.directfreight.com.au/ConsignmentStatus.aspx'
    return link


def changepurchaseorderstatus(request):
    if request.method == 'POST':
        list_of_drop_ship_order_line_id = []
        list_of_reorder_order_line_id = []

        pid = request.POST.get("pid")
        alias = request.POST.get("alias")
        trackingid = request.POST.get("trackingid")
        courier = request.POST.get("courier")
        internal_notes = request.POST.get("internal_notes")



        if ('save' in request.POST):

            for index, item in enumerate(request.POST.items()):
                if ("dropship" in item[0] and item[1] == 'False'):
                    drop_ship_order_line_id = item[0].split(":dropship")[0]

                    list_of_drop_ship_order_line_id.append(drop_ship_order_line_id)
                elif("reorder" in item[0] and item[1] == 'False'):
                    reorder_order_line_id = item[0].split(":reorder")[0]

                    list_of_reorder_order_line_id.append(reorder_order_line_id)


            try:
                purchase_order = purchaseorder.objects.get(purchase_orderid=str(pid))

                purchase_order.alias = alias
                purchase_order.tracking_id = trackingid
                purchase_order.courier = courier
                purchase_order.internal_notes=internal_notes
                purchase_order.save(update_fields=['alias'])
                purchase_order.save(update_fields=['tracking_id'])
                purchase_order.save(update_fields=['courier'])
                purchase_order.save(update_fields=['internal_notes'])

                messages.info(request, "Purchase Order Updated!")
            except:
                messages.info(request, "Alias Not Unique. Couldn't update")

            # Trying to update dropshiporderlineid
            if (len(list_of_drop_ship_order_line_id) > 0):
                orderline.objects.filter(order_line_id__in=list_of_drop_ship_order_line_id).update(
                    dropship=True)


            # Trying to update reorderlineid
            if (len(list_of_reorder_order_line_id) > 0):
                orderline.objects.filter(order_line_id__in=list_of_reorder_order_line_id).update(reorder=True)
                SupplierNew.objects.filter(order_line_id__in=list_of_reorder_order_line_id).update(reorder=True)



        elif ('submit' in request.POST):

            purchase_order = purchaseorder.objects.get(purchase_orderid=str(pid))
            if (purchase_order.submitted == False):
                purchase_order.submitted = True
                purchase_order.submitted_date = datetime.datetime.now().date()

                purchase_order.save(update_fields=['submitted'])
                purchase_order.save(update_fields=['submitted_date'])

                messages.info(request, "Purchase order submitted!")


        elif ('unsubmit' in request.POST):
            purchase_order = purchaseorder.objects.get(purchase_orderid=str(pid))
            if (purchase_order.submitted == True):
                purchase_order.submitted = False
                purchase_order.submitted_date = None

                purchase_order.save(update_fields=['submitted'])
                purchase_order.save(update_fields=['submitted_date'])

                messages.info(request, "Purchase order unsubmitted!")


        elif ('movetoday' in request.POST):
            purchase_order = purchaseorder.objects.get(purchase_orderid=str(pid))

            purchase_order.created_date = datetime.date.today()
            purchase_order.submitted = False
            purchase_order.submitted_date = None

            purchase_order.save(update_fields=['created_date'])
            purchase_order.save(update_fields=['submitted'])
            purchase_order.save(update_fields=['submitted_date'])

            messages.info(request, "Purchase order moved to today!")

        return redirect('/purchaseorder/?pid=' + str(pid))


def generatePurchaseOrder(request, supplier=None):
    dict_sku_orderid = {}

    if request.method == 'POST':
        with transaction.atomic():
            temp_dict = {}

            dict_of_post_items = request.POST.items()

            list_of_skus = []
            list_of_original_order_line_ids = []
            list_of_order_ids = []
            date = ""
            supplier_name = ""
            purchase_id_override = ""
            for index, item in enumerate(dict_of_post_items):
                tupple = item
                key = tupple[0]
                value = tupple[1]
                if not ("csrfmiddlewaretoken" == key):
                    if ("v_date" in key):
                        date = value
                    elif ("v_sup" in key):
                        supplier_name = value
                    elif ("purchase_id_override" in key):
                        purchase_id_override = value
                    elif ("sku" in key):
                        list_of_skus.append(value)
                    elif ("order_line_id" in key):
                        list_of_original_order_line_ids.append(value)
                    elif ("order" in key):
                        list_of_order_ids.append(value)

            # Contains the list of skus in the original order
            original_list_of_sku = list_of_skus

            for index2 in range(0, len(list_of_skus)):
                temp_list = []
                for temp in request.POST.items():
                    key1 = temp[0]
                    val1 = temp[1]
                    if not(key1 in ['csrfmiddlewaretoken','v_date' ,'v_sup','purchase_id_override']):
                        #Eg: key1 = 662815281;N10104354:sku
                        temp_key_sku=key1.split(";")[0]
                        temp_key_orderid=key1.split(";")[1]
                        temp_key_orderid=temp_key_orderid.split(":")[0]

                        if (list_of_skus[index2] ==temp_key_sku  and list_of_order_ids[index2] ==temp_key_orderid ):
                            temp_list.append(val1)

                temp_dict[(list_of_skus[index2], list_of_order_ids[index2])] = temp_list

            list_of_skus = []
            list_of_order_line_ids = []
            list_of_partnumbers = []
            list_of_qty = []
            list_of_in_stock = []
            for item in temp_dict:
                sku = temp_dict[item][0]
                order_id = temp_dict[item][1]
                order_line_id = temp_dict[item][2]

                part_number = temp_dict[item][4]
                qty = temp_dict[item][5]
                stock = qty

                list_of_order_line_ids.append(order_line_id)
                list_of_skus.append(sku)
                list_of_partnumbers.append(part_number)
                list_of_qty.append(qty)
                list_of_in_stock.append(stock)

            date = datetime.date.today()

            date2 = str(datetime.datetime.today()).replace("-", "").split(".")[0].replace(":", "").replace(" ", "")
            if (len(supplier_name) > 3):
                supplier_name2 = supplier_name[:3]
            else:
                supplier_name2 = supplier_name

            #Checking is a supplier has been marked as disabled.Proceed only if disabled=False
            supplier_status_object=Supplier_Details.objects.get(
                short_code=supplier_name)
            supplier_status_disabled=supplier_status_object.disabled
            if not(supplier_status_disabled):

                # Handling overidden purchase order ID
                if (purchase_id_override != ""):
                    # try:

                    # looking for purchase order if it exists
                    try:
                        purchase_order = purchaseorder.objects.get(purchase_orderid=str(purchase_id_override),
                                                                   supplier_name=Supplier_Details.objects.get(
                                                                       short_code=supplier_name), submitted=False)
                        if (purchase_order.purchase_orderid == purchase_id_override):

                            ####new

                            batch = []

                            for index in range(0, len(list_of_original_order_line_ids)):

                                orderlineid = list_of_original_order_line_ids[index]
                                sku = original_list_of_sku[index]
                                part_number = list_of_partnumbers[index]
                                qty = list_of_qty[index]
                                stock = list_of_in_stock[index]

                                try:
                                    # trying to look for already inserted
                                    order = orderline.objects.get(order_line_id=orderlineid)
                                except:
                                    query = orderline(order_line_id=orderlineid, sku=sku, part_number=part_number, qty=qty,
                                                      instock=stock,
                                                      purchase_orderid=purchaseorder.objects.get(
                                                          purchase_orderid=str(purchase_id_override)))

                                    batch.append(query)
                                    # print(orderlineid, "Inserted!", index)

                            batch_size = 50
                            orderline.objects.bulk_create(batch, batch_size)
                            ###New code end

                            # Adding the order ids
                            batch = []
                            for index in range(0, len(list_of_order_ids)):
                                orderid = list_of_order_ids[index]
                                sku = original_list_of_sku[index]
                                order_line_id = list_of_original_order_line_ids[index]
                                try:
                                    # Trying to look for already inserted
                                    orderid_purid = orderid_purchaseorderid.objects.get(order_id=str(orderid), sku=sku,
                                                                                        order_line_id=order_line_id,
                                                                                        purchase_orderid=str(
                                                                                            purchase_id_override))
                                except:
                                    query = orderid_purchaseorderid(
                                        order_id=orderid,
                                        sku=sku,
                                        order_line_id=order_line_id,
                                        purchase_orderid=purchaseorder.objects.get(purchase_orderid=str(purchase_id_override)))
                                    batch.append(query)

                            batch_size = 50
                            orderid_purchaseorderid.objects.bulk_create(batch, batch_size)

                            SupplierNew.objects.filter(order_line_id__in=list_of_original_order_line_ids).update(
                                purchase_order_generated=True)

                            return redirect('/purchaseorder')


                    except:

                        return redirect('/purchaseorder')


                else:
                    # Creating new purchase order
                    purchase_id = str(supplier_name2) + str(date2)
                    enterDataPurchaseIDOrder(purchase_id, supplier_name, date, list_of_qty, list_of_in_stock,
                                             list_of_partnumbers, list_of_order_ids, original_list_of_sku,
                                             list_of_original_order_line_ids)

                    return redirect('/purchaseorder/?pid=' + str(purchase_id))
            else:
                return redirect('/purchaseorder')

    else:
        return shownewpurchaseorderdetails(request, supplier)


def enterDataPurchaseIDOrder(purchase_id, supplier_name, date, list_of_qty, list_of_in_stock,
                             list_of_partnumbers, list_of_order_ids, list_of_original_sku,
                             list_of_original_order_line_ids):
    try:
        # Trying to look for already inserted
        purchase_order = purchaseorder.objects.get(purchase_orderid=purchase_id)

    except:

        purchase_order = purchaseorder(purchase_orderid=purchase_id,
                                       supplier_name=Supplier_Details.objects.get(short_code=supplier_name),
                                       created_date=date,
                                       tracking_id="NA",
                                       courier="NA",
                                       alias=purchase_id, legacy_purchase_id=False
                                       )
        purchase_order.save()

    batch = []
    for index in range(0, len(list_of_order_ids)):
        orderid = list_of_order_ids[index]
        sku = list_of_original_sku[index]
        order_line_id = list_of_original_order_line_ids[index]

        try:
            # Trying to look for already inserted
            orderid_purid = orderid_purchaseorderid.objects.get(order_id=str(orderid),
                                                                sku=sku,
                                                                order_line_id=order_line_id,
                                                                purchase_orderid=str(purchase_id))

        except:

            query = orderid_purchaseorderid(
                order_id=orderid,
                sku=sku,
                order_line_id=order_line_id,
                purchase_orderid=purchaseorder.objects.get(purchase_orderid=str(purchase_id)))
            batch.append(query)

    batch_size = 50
    orderid_purchaseorderid.objects.bulk_create(batch, batch_size)
    SupplierNew.objects.filter(order_line_id__in=list_of_original_order_line_ids).update(
        purchase_order_generated=True)

    ####new

    batch = []
    for index in range(0, len(list_of_original_order_line_ids)):

        orderlineid = list_of_original_order_line_ids[index]
        sku = list_of_original_sku[index]
        part_number = list_of_partnumbers[index]
        qty = list_of_qty[index]
        stock = list_of_in_stock[index]

        try:
            # trying to look for already inserted
            order = orderline.objects.get(order_line_id=orderlineid)
        except:
            query = orderline(order_line_id=orderlineid, sku=sku, part_number=part_number, qty=qty, instock=stock,
                              purchase_orderid=purchaseorder.objects.get(purchase_orderid=str(purchase_id)))

            batch.append(query)

    batch_size = 50
    orderline.objects.bulk_create(batch, batch_size)
    ###New code end


def create_excel(list_of_skus, dict_of_brand_name_sku, list_of_quantity, list_of_part_number, purchase_order_id,
                 purchase_order_submitted_alias, list_of_instock, checklist=False):
    output = BytesIO()

    wb = Workbook(output)

    ws = wb.add_worksheet('Sheet1')
    # row , column , data
    created_date = datetime.datetime.now()
    created_date = created_date.date()
    purchaseid = purchase_order_submitted_alias

    ws.write(0, 2, 'Purchase Order',
             wb.add_format({'bold': True, 'font_color': '', 'font_size': '18', 'font_name': 'Arial'}))

    ws.write(1, 2, 'SHIP TO:', wb.add_format({'bold': True, 'font_color': '', 'font_size': '11', 'font_name': 'Arial'}))
    ws.write(2, 2, 'FIND SPORTS', wb.add_format({'font_size': '11', 'font_name': 'Arial'}))
    ws.write(3, 2, '4 MAXWELL STREET')
    ws.write(4, 2, 'DANDENONG SOUTH, VIC 3175')

    ws.write(0, 3, str(created_date),
             wb.add_format({'bold': True, 'font_color': '', 'font_size': '11', 'font_name': 'Arial'}))
    ws.write(1, 3, purchaseid)

    cell_format = wb.add_format()
    cell_format.set_bg_color('#ffcc9c')
    cell_format.set_bold()
    ws.write(8, 0, 'SKU', cell_format)

    last_row = 5 + len(list_of_skus)

    cell_format_out_of_stock = wb.add_format()
    cell_format_out_of_stock.set_pattern(1)
    cell_format_out_of_stock.set_bg_color('#e83a3a')

    col_index = 0
    for index in range(0, len(list_of_skus)):
        if (list_of_instock[index] == 'True' or list_of_instock[index] == list_of_quantity[index]):
            ws.write(9 + index, col_index, list_of_skus[index])
        else:
            ws.write(9 + index, col_index, list_of_skus[index], cell_format_out_of_stock)

    if (checklist == False):
        col_index += 1
        ws.write(8, col_index, 'Brands', cell_format)

        for index in range(0, len(list_of_skus)):
            sku = list_of_skus[index]
            if (list_of_instock[index] == 'True' or list_of_instock[index] == list_of_quantity[index]):
                ws.write(9 + index, col_index, dict_of_brand_name_sku[sku]['Brand'])
            else:
                ws.write(9 + index, col_index, dict_of_brand_name_sku[sku]['Brand'], cell_format_out_of_stock)

    col_index += 1
    if (checklist == False):
        ws.set_column(8, col_index, 40)
    ws.write(8, col_index, 'Product Description', cell_format)

    for index in range(0, len(list_of_skus)):
        sku = list_of_skus[index]
        if (list_of_instock[index] == 'True' or list_of_instock[index] == list_of_quantity[index]):
            ws.write(9 + index, col_index, dict_of_brand_name_sku[sku]['Name'])
        else:
            ws.write(9 + index, col_index, dict_of_brand_name_sku[sku]['Name'], cell_format_out_of_stock)

    col_index += 1
    ws.write(8, col_index, 'Quantity', cell_format)
    totalqty = 0
    for index in range(0, len(list_of_quantity)):
        if (list_of_instock[index] == 'True' or list_of_instock[index] == list_of_quantity[index]):
            ws.write(9 + index, col_index, list_of_quantity[index])
        else:
            ws.write(9 + index, col_index, list_of_quantity[index], cell_format_out_of_stock)
        totalqty = totalqty + int(list_of_quantity[index])

    col_index += 1
    ws.write(8, col_index, 'Part Number', cell_format)

    for index in range(0, len(list_of_skus)):
        if (list_of_instock[index] == 'True' or list_of_instock[index] == list_of_quantity[index]):
            ws.write(9 + index, col_index, list_of_part_number[index])
        else:
            ws.write(9 + index, col_index, list_of_part_number[index], cell_format_out_of_stock)

    ws.write(9 + last_row, 0, '', cell_format)
    ws.write(9 + last_row, 1, '', cell_format)
    ws.write(9 + last_row, 2, '', cell_format)
    ws.write(9 + last_row, 3, totalqty, cell_format)
    if (checklist == False):
        ws.write(9 + last_row, 4, '', cell_format)

    ws.write(9 + last_row + 1, 2, 'Ps. All double ups are legit',
             wb.add_format({'bold': True, 'font_color': 'red', 'font_size': '11', 'font_name': 'Arial'}))
    ws.write(9 + last_row + 2, 2, 'If a product is out of stock, please give us notification and CANCEL it.',
             wb.add_format({'bold': True, 'font_color': 'red', 'font_size': '11', 'font_name': 'Arial'}))

    wb.close()

    output.seek(0)

    # Set up the Http response.
    filename = purchase_order_submitted_alias + '.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


def search_and_return_purchaseid_alias(purchaseid_alias_orderid):
    try:
        p_order = purchaseorder.objects.filter(
            Q(purchase_orderid=str(purchaseid_alias_orderid)) | Q(alias=str(purchaseid_alias_orderid)))
        purchase_orderid = [result.purchase_orderid for result in p_order][0]

        return redirect('/purchaseorder/?pid=' + str(purchase_orderid))
    except:
        return redirect('/')


def viewalluncheckedpurchaseorders(isWarehouse=False):
    if not (isWarehouse):
        supplierdetails = Supplier_Details.objects.filter(website_order_placement=True)
        list_of_website_order_supplier_names = [result.supplier_name for result in supplierdetails]

        uncheckedpurchaseorders = purchaseorder.objects.filter(stock_confirmed=False, submitted=True,
                                                               legacy_purchase_id=False,
                                                               supplier_name__in=list_of_website_order_supplier_names)
    else:

        uncheckedpurchaseorders = purchaseorder.objects.filter(submitted=True,
                                                               legacy_purchase_id=False, received=False,
                                                               )


    List_of_unchecked_purchase_order_ids = [result.purchase_orderid for result in uncheckedpurchaseorders]


    if(len(List_of_unchecked_purchase_order_ids)>0):

        dict_purchase_order_submitted_date = {}
        list_of_purchase_orders = []
        for singleorder in uncheckedpurchaseorders:

            temp_dict = {}
            business_days=int(np.busday_count(singleorder.submitted_date, today_date))
            if(business_days<0):
                business_days=0
            temp_tupple = (singleorder.alias, singleorder.submitted_date, singleorder.purchase_orderid,
                           business_days)
            dict_purchase_order_submitted_date[singleorder.alias] = temp_tupple

        ####

        List_of_confirm_pending = [(alias, submitted_date, pid, days) for alias, submitted_date, pid, days in
                                   dict_purchase_order_submitted_date.values()]


        list1 = list(map(list, zip(*List_of_confirm_pending)))


        List_of_confirm_pending = zip(list1[0], list1[1], list1[2], list1[3])
        List_of_confirm_pending = list(List_of_confirm_pending)

        List_of_confirm_pending = sorted(List_of_confirm_pending, key=lambda x: x[3], reverse=True)

        return List_of_confirm_pending
    else:
        return []


def viewPendingSubmitCreatedPurchaseOrders():
    dict_pending_submit = {}
    unsubmitted_orders = purchaseorder.objects.filter(created_date__isnull=False, submitted=False,
                                                      legacy_purchase_id=False)

    for order in unsubmitted_orders:
        if ((np.busday_count(order.created_date, today_date)) >= 0):
            business_days = str(np.busday_count(order.created_date, today_date))
        else:
            business_days = str(0)
        dict_pending_submit[order.alias] = (
            order.alias, business_days, order.created_date, order.purchase_orderid,
            getattr(order.supplier_name, 'supplier_name'))

    error_count_pending_submit = 0
    List_of_submit_pending = [(alias, days, date, order, supplier_name) for alias, days, date, order, supplier_name in
                              dict_pending_submit.values()]
    list1 = list(map(list, zip(*List_of_submit_pending)))
    if (len(list1) > 0):
        for index in range(0, len(list1[1])):
            if not (list1[1][index] == 0):
                list1[1][index] = int(list1[1][index].split(" ")[0].replace("0:00:00", "0"))

        for temp in list1[1]:
            if (temp >= 3):
                error_count_pending_submit += 1

        List_of_submit_pending = zip(list1[0], list1[1], list1[2], list1[3], list1[4])
        List_of_submit_pending = list(List_of_submit_pending)

    List_of_submit_pending = sorted(List_of_submit_pending, key=lambda x: x[1], reverse=True)
    return List_of_submit_pending


def subpurchaseorders(request):
    if request.method == 'GET':
        try:
            pid = request.GET.get('pid')

            sub_po = sub_purchaseorder.objects.filter(purchase_orderid=pid)
            list_of_subpurchaseorderids = []
            dict_sub_poid_details = {}
            for temp in sub_po:
                list_of_subpurchaseorderids.append(temp.sub_purchaseorderid)

                temp_dict = {}
                temp_dict['alias'] = temp.alias
                if (temp.courier == None):
                    temp_dict['courier'] = "NA"
                else:
                    temp_dict['courier'] = temp.courier

                if (temp.tracking_id == None):
                    temp_dict['trackingid'] = "NA"
                else:
                    temp_dict['trackingid'] = temp.tracking_id

                dict_sub_poid_details[temp.sub_purchaseorderid] = temp_dict

            dict_subpoid_details = {}
            orderlineids = orderline.objects.filter(sub_purchaseorderid__in=list_of_subpurchaseorderids)
            list_of_order_line_ids = []
            dict_orderline_id_subpurchaseorderid = {}
            for temp2 in orderlineids:
                temp_dict2 = {}
                sub_poid = getattr(temp2.sub_purchaseorderid, 'sub_purchaseorderid')
                temp_dict2['subpoid'] = sub_poid
                temp_dict2['orderlineid'] = temp2.order_line_id

                dict_orderline_id_subpurchaseorderid[temp2.order_line_id] = sub_poid

                list_of_order_line_ids.append(temp2.order_line_id)
                temp_dict2['sku'] = temp2.sku
                temp_dict2['qty'] = temp2.qty
                temp_dict2['stock'] = temp2.instock
                temp_dict2['partnumber'] = temp2.part_number
                temp_dict2['alias'] = dict_sub_poid_details[sub_poid]['alias']
                temp_dict2['courier'] = dict_sub_poid_details[sub_poid]['courier']
                temp_dict2['trackingid'] = dict_sub_poid_details[sub_poid]['trackingid']

                temp_dict2['purchaseorderid'] = getattr(temp2.purchase_orderid, 'purchase_orderid')

                dict_subpoid_details[getattr(temp2.sub_purchaseorderid, 'sub_purchaseorderid')] = temp_dict2

            orderid_details = orderid_purchaseorderid.objects.filter(order_line_id__in=list_of_order_line_ids)

            dict_orderlineid_details = {}
            list_of_outputvariables = ["ShipFirstName", "ShipLastName", "ShippingOption", "ShipStreetLine1", "ShipCity",
                                       "ShipState", "ShipCountry", "ShippingSignature", "ShipPhone",
                                       "DeliveryInstruction",
                                       "ShipPostCode"]
            for temp3 in orderid_details:
                response_dict = api_order_response({"OrderID": temp3.order_id}, None, None)['Order'][0]
                response_dict = {your_key: response_dict[your_key] for your_key in list_of_outputvariables}

                for temp_4 in list_of_outputvariables:
                    dict_subpoid_details[dict_orderline_id_subpurchaseorderid[temp3.order_line_id]][temp_4] = \
                        response_dict[
                            temp_4]

            return render(request, 'purchaseorder/subpurchaseorder.html',
                          {"list_of_subpurchaseorderids": list_of_subpurchaseorderids,
                           "dict_subpoid_details": dict_subpoid_details})
        except:
            redirect("/purchaseorder")
    else:
        return HttpResponse("No pid")

@login_required
def index(request):
    newPurchaseOrder = request.GET.get('newPurchaseOrder')
    supplier = request.GET.get('supplier')
    generate = request.GET.get('generate')

    purchaseid_alias = request.GET.get('purchaseid_alias')

    supplier_name_searching = request.GET.get('supplier_name')


    if (purchaseid_alias != None):

        return search_and_return_purchaseid_alias(purchaseid_alias)
    else:

        if (newPurchaseOrder != None and supplier != None and generate != None):

            return generatePurchaseOrder(request, supplier)
            # return generatePurchaseOrder(request,supplier)
        elif (newPurchaseOrder != None):

            # Display the list of unique suppliers here!
            return createNewPurchaseOrder(request)


        else:

            p_id = request.GET.get('pid')
            if not (p_id is None):
                # When a purchase id exists in the header
                return viewpurchaseorder(request, p_id)

            else:

                # Displaying unique dates
                created_on = request.GET.get('created_on')
                if not (created_on is None):
                    # Date filter passed , show all purchase ids on that date

                    date_time_obj = datetime.datetime.strptime(created_on, '%b. %d, %Y')
                    return viewallpurchaseorders(request, date_time_obj)


                else:
                    # No date filter is passed . Show all available created on dates

                    list_of_unique_dates = viewallpurchaseorders(request)
                    list_of_submit_pending = viewPendingSubmitCreatedPurchaseOrders()
                    dict_purchase_order_submitted_date = viewalluncheckedpurchaseorders()



                    if (supplier_name_searching != None):
                        # # Display a list of all purchase orders with their dates for that supplier
                        # purchase_order_object = purchaseorder.objects.filter(supplier_name=Supplier_Details.objects.get(
                        #     supplier_name=supplier_name_searching))
                        #
                        # List_of_purchase_order_with_dates = [(result.alias, result.submitted_date) for result in
                        #                                      purchase_order_object]
                        #
                        # print(List_of_purchase_order_with_dates)



                        return render(request, 'purchaseorder/purchaseorders.html',
                                      {"unique_dates": True, "list_of_submit_pending": list_of_submit_pending,
                                       "list_of_unique_dates": sorted(list_of_unique_dates, reverse=True),
                                       "dict_purchase_order_submitted_date": dict_purchase_order_submitted_date
                                       })


                    else:
                        # Showing all purchase orders based on supplier name
                        # purchase_order_object = purchaseorder.objects.all()
                        # List_of_unique_suppliers = [result.supplier_name for result in
                        #                             purchase_order_object]
                        # List_of_unique_suppliers = list(set(List_of_unique_suppliers))


                        return render(request, 'purchaseorder/purchaseorders.html',
                                      {"unique_dates": True, "list_of_submit_pending": list_of_submit_pending,
                                       "list_of_unique_dates": sorted(list_of_unique_dates, reverse=True),
                                       "dict_purchase_order_submitted_date": dict_purchase_order_submitted_date})
