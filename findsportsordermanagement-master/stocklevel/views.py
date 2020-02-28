from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
import requests
from fusioncharts import FusionCharts
from collections import OrderedDict

from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response

@login_required
def index(request):
    List_of_suppliers = ["AbsoluteBoard", "Ansco", "Bentley Sports", "Bolle", "CB", "Columbia_2",
                         "Companion", "Country_Outfiitters", "Dropshipzone", "FIND_Imports", "Globe",
                         "HGB", "JetPilot", "Liive", "LushProductions", "Mares", "Nitro", "oe_2",
                         "PhoenixLeisureGroup", "ProjectDistribution", "Quattro_Sports", "ROJO", "Rosbert", "Spelean",
                         "Thule", "Zen", "XTM"]

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
                          supplier.replace("Country_Outfiitters", "Country Outfiitters").replace("Quattro_Sports",
                                                                                                 "Quattro Sports").replace(
                              "FIND_Imports", "Find Sports").replace("oe_2", "Ocean Earth 2").replace("Columbia_2",
                                                                                                      "Columbia 2"),
                          float(percentage)))

    temp_list = sorted(temp_list, key=lambda x: x[4], reverse=True)

    return render(request, 'stocklevel.html',
                  {"dashboard": False, "orders": False, "stocklevel": True, "suppliers_qty": temp_list})
