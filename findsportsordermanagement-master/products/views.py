from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
import requests
from django.http import HttpResponse, HttpResponseNotFound
from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response

@login_required
def index(request, sku):
    if request.method == 'GET':
        dict_input_filter = {"SKU": sku}
        json1_data = api_product_response(dict_input_filter)

        dict_of_product_details = json1_data['Item']
        product_dict = {}
        for index in range(0, len(dict_of_product_details)):
            data = dict_of_product_details[index]
            product_dict[sku] = data

        return render(request, 'products.html', {"product_details": product_dict})
    else:
        return HttpResponseNotFound('<h1>INVALID REQUEST</h1>')
