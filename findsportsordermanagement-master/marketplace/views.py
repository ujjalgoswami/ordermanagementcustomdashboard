import csv
import os

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse

import findsportsordermanagement.settings as settings
from django.shortcuts import render, redirect
from django.contrib import messages
import io
import json
import pandas as pd
import requests

from django.http import HttpResponse
from collections import OrderedDict

from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response

# Include the `fusioncharts.py` file that contains functions to embed the charts.
from fusioncharts import FusionCharts


@login_required
def index(request):
    # For File download
    file_type_to_download = request.GET.get('download')
    if (file_type_to_download):
        list_of_order_ids = []
        list_of_business_days = []
        list_of_invoice_date = []

        if (file_type_to_download == 'catchpendingproducts'):

            url2 = "https://www.findsports.com.au/export/ordermanagementdashboard/approved_for_catch.csv"

            payload2 = ""
            headers2 = {
                'cache-control': "no-cache",
                'Postman-Token': "a5e0c8d8-94a3-4e0a-80ed-d334cae24150"
            }

            response2 = requests.request("GET", url2, data=payload2, headers=headers2)

            temp_list_2 = response2.text.split("\r\n")
            list_of_primary_supplier_name = []
            list_of_skus = []
            list_of_qtys = []
            list_of_approved = []
            list_of_active = []

            for index in range(1, len(temp_list_2) - 1):
                temp_list3 = temp_list_2[index].replace("\"", "").replace("Zen Imports Pty Ltd,", "Zen").split(",")

                list_of_active.append(temp_list3[0])
                list_of_approved.append(temp_list3[1])
                list_of_skus.append(temp_list3[2])
                list_of_primary_supplier_name.append(temp_list3[3])
                list_of_qtys.append(temp_list3[4])

            # list_of_qtys = list(map(int, list_of_qtys))
            for index in range(0, len(list_of_qtys)):
                list_of_qtys[index] = int(list_of_qtys[index])

            columns2 = ['Approved for Catch', 'SKU*', 'Primary Supplier Name', 'QTY']
            df_neto_all_products_status = pd.DataFrame(columns=columns2)
            df_neto_all_products_status['Primary Supplier Name'] = list_of_primary_supplier_name
            df_neto_all_products_status['QTY'] = list_of_qtys
            df_neto_all_products_status['Approved for Catch'] = list_of_approved
            df_neto_all_products_status['SKU*'] = list_of_skus

            df_neto_all_products_status = df_neto_all_products_status[
                (df_neto_all_products_status['Approved for Catch'] == 'y')]

            list_of_approved_skus = list(df_neto_all_products_status['SKU*'])
            list_of_approved_suppliers = list(df_neto_all_products_status['Primary Supplier Name'])

            filename = settings.STATIC_ROOT + '/datafiles/' + 'catch_exported_offers.csv'
            df_catch_exported_offers = pd.read_csv(filename)

            list_of_catch_skus = list(df_catch_exported_offers['Offer SKU'])

            list_of_missing_skus = []
            list_of_missing_supplier = []
            for index2 in range(0, len(list_of_approved_skus)):
                if not (list_of_approved_skus[index2] in list_of_catch_skus):
                    list_of_missing_skus.append(list_of_approved_skus[index2])
                    list_of_missing_supplier.append(list_of_approved_suppliers[index2])

            filename = "Catch_Pending_Products"

            columns = ['SKU', 'SupplierName']

            df = pd.DataFrame(columns=columns)
            df['SKU'] = list_of_missing_skus
            df['SupplierName'] = list_of_missing_supplier

            response = HttpResponse(content_type='text/csv')

            response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'

            df.to_csv(path_or_buf=response, index=False)

            return response

    return render(request, 'marketplace/marketplace.html', {"marketplace": True})


def viewjsonerrors(request):
    filename = settings.STATIC_ROOT + '/datafiles/' + 'ALLPRODSHUGE_output_error.csv'
    df_errors = pd.read_csv(filename)

    df_errors['Primary Supplier Name'].replace('Home Grown Brands', 'HGB', inplace=True)
    df_errors['Primary Supplier Name'].replace('Cape Byron', 'CB', inplace=True)
    df_errors['Primary Supplier Name'].replace('FIND Imports', 'FIND_Imports', inplace=True)
    df_errors['Primary Supplier Name'].replace('Companion Brands', 'Companion', inplace=True)
    df_errors['Primary Supplier Name'].replace('JetPilot', 'JetPilot', inplace=True)
    df_errors['Primary Supplier Name'].replace('OceanEarth_2', 'oe_2', inplace=True)
    df_errors['Primary Supplier Name'].replace('AbsoluteBoard', 'AbsoluteBoard', inplace=True)
    df_errors['Primary Supplier Name'].replace('Zen Imports Pty Ltd,', 'Zen', inplace=True)

    list_of_unique_comments = list(set(list(df_errors["comments"])))
    list_of_unique_suppliers = list(set(list(df_errors["Primary Supplier Name"])))

    temp_list = []
    temp_list2 = []
    total_errors = 0
    list_of_ids = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    for index in range(0, len(list_of_unique_comments)):
        comment = list_of_unique_comments[index]
        temp_dict = {}

        temp_dict["label"] = comment
        temp_dict["value"] = len(df_errors[(df_errors['comments'] == comment)])
        temp_dict["link"] = "newchart-xml-" + str(list_of_ids[index])
        total_errors = total_errors + int(len(df_errors[(df_errors['comments'] == comment)]))
        temp_list.append(temp_dict)

        temp_dict2 = {}
        temp_dict2["id"] = str(list_of_ids[index])

        temp_dict3 = {}
        temp_dict4 = {}

        temp_dict4["caption"] = comment
        temp_dict4["subcaption"] = "Products with error"
        temp_dict4["xaxisname"] = "Suppliers"
        temp_dict4["yaxisname"] = "Number of Products"
        temp_dict4["numberprefix"] = ""
        temp_dict4["theme"] = "fusion"
        temp_dict4["rotateValues"] = "0"

        temp_dict3["chart"] = temp_dict4
        temp_list3 = []

        for index2 in range(0, len(list_of_unique_suppliers)):
            temp_dict5 = {}
            supplier = list_of_unique_suppliers[index2]

            temp_dict5["label"] = supplier
            temp_dict5["value"] = len(
                df_errors[(df_errors['comments'] == comment) & (df_errors['Primary Supplier Name'] == supplier)])

            temp_list3.append(temp_dict5)

        temp_dict3["data"] = temp_list3

        temp_dict2["linkedchart"] = temp_dict3

        temp_list2.append(temp_dict2)

    data = {
        "type": 'column2d',
        "renderAt": 'chart-container3',
        "width": '800',
        "height": '600',
        "dataFormat": 'json',
        "dataSource": {
            "chart": {
                "caption": "Types of Errors",
                "subcaption": "Select one to view affected suppliers",
                "xaxisName": "Types of errors",
                "yaxisName": "Number of affected products",
                "numberPrefix": "",
                "theme": "fusion"
            },
            "data": temp_list,
            "linkeddata": temp_list2
        }
    }

    return JsonResponse(data)


def viewjson(request):
    List_of_tuples = calculate_suppliers_stock_levels()

    columns = ["SKU", 'SUPPLIER']
    df = pd.DataFrame(columns=columns)
    list_of_active_products = []
    list_of_supplier_name = []
    for index in range(0, len(List_of_tuples)):
        list_of_active_products.append(int(List_of_tuples[index][0]) - int(List_of_tuples[index][2]))
        list_of_supplier_name.append(List_of_tuples[index][3])

    url2 = "https://www.findsports.com.au/export/ordermanagementdashboard/approved_for_catch.csv"

    payload2 = ""
    headers2 = {
        'cache-control': "no-cache",
        'Postman-Token': "a5e0c8d8-94a3-4e0a-80ed-d334cae24150"
    }

    response2 = requests.request("GET", url2, data=payload2, headers=headers2)

    temp_list_2 = response2.text.split("\r\n")
    list_of_primary_supplier_name = []
    list_of_skus = []
    list_of_qtys = []
    list_of_approved = []
    list_of_active = []

    for index in range(1, len(temp_list_2) - 1):
        temp_list3 = temp_list_2[index].replace("\"", "").replace("Zen Imports Pty Ltd,", "Zen").split(",")

        list_of_active.append(temp_list3[0])
        list_of_approved.append(temp_list3[1])
        list_of_skus.append(temp_list3[2])
        list_of_primary_supplier_name.append(temp_list3[3])
        list_of_qtys.append(temp_list3[4])

    # list_of_qtys = list(map(int, list_of_qtys))
    for index in range(0, len(list_of_qtys)):
        try:
            list_of_qtys[index] = int(list_of_qtys[index])
        except:
            print(list_of_qtys[index])

    columns2 = ['Active', 'Approved for Catch', 'SKU*', 'Primary Supplier Name', 'QTY']
    df_neto_all_products_status = pd.DataFrame(columns=columns2)
    df_neto_all_products_status['Primary Supplier Name'] = list_of_primary_supplier_name
    df_neto_all_products_status['QTY'] = list_of_qtys
    df_neto_all_products_status['Approved for Catch'] = list_of_approved

    df_neto_all_products_status['Primary Supplier Name'].replace('Home Grown Brands', 'HGB', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('Cape Byron', 'CB', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('FIND Imports', 'FIND_Imports', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('Companion Brands', 'Companion', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('JetPilot', 'JetPilot', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('OceanEarth_2', 'oe_2', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('AbsoluteBoard', 'AbsoluteBoard', inplace=True)
    df_neto_all_products_status['Primary Supplier Name'].replace('Zen Imports Pty Ltd,', 'Zen', inplace=True)

    filename = settings.STATIC_ROOT + '/datafiles/' + 'catch_exported_offers.csv'
    df_catch_exported_offers = pd.read_csv(filename)

    list_of_sku_catch = list(df_catch_exported_offers["Offer SKU"])
    list_of_activated_catch = list(df_catch_exported_offers["Activated"])

    json1_data = api_product_response({"SKU": list_of_sku_catch}, ["SKU", "PrimarySupplier"])
    list_of_items = json1_data['Item']

    dict_of_sku_primary_supplier = {}

    for index in range(0, len(list_of_items)):
        dict_of_sku_primary_supplier[list_of_items[index]['SKU']] = list_of_items[index]['PrimarySupplier']

    list_of_primary_suppliers = []

    for index in range(0, len(list_of_sku_catch)):
        list_of_primary_suppliers.append(dict_of_sku_primary_supplier[list_of_sku_catch[index]])

    df_catch_exported_offers['SUPPLIER'] = list_of_primary_suppliers

    list_of_unique_catch_suppliers = list(set(list_of_primary_suppliers))

    # setting categories
    dict_categ = {}

    temp_list = []
    list_of_total_catch = []
    list_of_active = []
    list_of_find_catch_approved = []
    list_of_find_active = []
    for index in range(0, len(list_of_supplier_name)):
        tempdict = {}

        tempdict["label"] = list_of_supplier_name[index]
        temp_list.append(tempdict)
        tempdict = {}
        tempdict["value"] = list_of_active_products[index]
        list_of_find_active.append(tempdict)

        tempdict = {}
        tempdict["value"] = len(df_catch_exported_offers[
                                    (df_catch_exported_offers['SUPPLIER'] == list_of_supplier_name[index]) & (
                                            df_catch_exported_offers['Quantity'] > 0)])
        list_of_total_catch.append(tempdict)

        tempdict = {}
        tempdict["value"] = len(df_neto_all_products_status[(df_neto_all_products_status['Primary Supplier Name'] ==
                                                             list_of_supplier_name[index]) & (
                                                                    df_neto_all_products_status[
                                                                        'Approved for Catch'] == 'y') & (
                                                                    df_neto_all_products_status['QTY'] > 0)])
        list_of_find_catch_approved.append(tempdict)

    dict_categ['category'] = temp_list

    data = {
        'type': 'mscolumn2d',
        'renderAt': 'chart-container',
        'width': '800',
        'height': '600',
        'dataFormat': 'json',
        'dataSource': {
            "chart": {
                "theme": "fusion",
                "caption": "Catch In Stock Products Status",
                "xAxisname": "Suppliers",
                "yAxisName": "Number of Products",
                "numberPrefix": "",
                "plotFillAlpha": "80",
                "divLineIsDashed": "1",
                "divLineDashLen": "1",
                "divLineGapLen": "1",
                "exportEnabled": "1",
                "exportMode": "client"
            },
            "categories": [dict_categ],
            "dataset": [
                {
                    "seriesname": "FINDSPORTS ACTIVE",
                    "data": list_of_find_active
                },
                {
                    "seriesname": "FIND CATCH APPROVED",
                    "data": list_of_find_catch_approved
                },
                {
                    "seriesname": "CATCH CURRENT",
                    "data": list_of_total_catch
                }
            ]
        }
    }

    return JsonResponse(data, json_dumps_params={'indent': 2})


def file_upload(request):
    prompt = {
        'order': 'This is a demo message error'
    }
    if request.method == 'GET':
        return render(request, "marketplace/marketplace.html", prompt)

    csv_file = request.FILES['file']

    if not (csv_file.name.endswith('.csv')):
        messages.error(request, "This is not a csv file")

    context = {}

    return render(request, "marketplace/marketplace.html", context)


def calculate_suppliers_stock_levels():
    List_of_suppliers = ["AbsoluteBoard", "CB", "Columbia_2",
                         "Companion", "FIND_Imports",
                         "HGB", "JetPilot", "oe_2", "Rosbert", "Spelean", "Zen", "XTM","Mizu"]

    dict_input_filter = {"IsActive": "True", "PrimarySupplier": List_of_suppliers}
    json1_data = api_product_response(dict_input_filter,
                                      ["SKU", "AvailableSellQuantity", "PrimarySupplier", "DateUpdated"])

    dict_of_order_details = json1_data['Item']

    dict_of_suppliers_qty = {}
    temp_list = []

    for supplier in List_of_suppliers:
        out_of_stock_counter = 0
        total_active_items = 0
        back_order_items = 0

        for index in range(0, len(dict_of_order_details)):
            data = dict_of_order_details[index]

            primary_supplier = data['PrimarySupplier']

            if (primary_supplier == supplier):

                qty = data['AvailableSellQuantity']

                if (int(qty) == 0):
                    out_of_stock_counter += 1
                elif (int(qty) < 0):
                    back_order_items += 1
                    out_of_stock_counter += 1

                total_active_items += 1

        if (total_active_items == 0):
            percentage = 0
        elif (out_of_stock_counter == 0):
            percentage = 0
        else:
            percentage = str((out_of_stock_counter / total_active_items) * 100)[:5]

        dict_of_suppliers_qty[supplier] = {"TotalActive": total_active_items, "BackOrder": back_order_items,
                                           "OutofStock": out_of_stock_counter,
                                           "Percentage": percentage, "name": supplier}

        temp_list.append((total_active_items, back_order_items, out_of_stock_counter,
                          supplier, float(percentage)))

    temp_list = sorted(temp_list, key=lambda x: x[4], reverse=True)
    return temp_list

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage('assets/datafiles')
        if os.path.isfile('assets/datafiles/catch_exported_offers.csv'):
            os.remove('assets/datafiles/catch_exported_offers.csv')
        filename = fs.save('catch_exported_offers.csv', myfile)
        return redirect('/marketplace')
    return redirect('/marketplace')