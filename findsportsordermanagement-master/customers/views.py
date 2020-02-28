from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from customers.models import Customers
from netoapihook.models import OrderHistory
import pandas as pd

@login_required
def index(request):
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

    # Getting the details of the customers who have had their orders delivered in 7 days or less
    shipped_customers = Customers.objects.filter(order_id__in=list_of_happy_order_ids)

    result_ids = [result.order_id for result in shipped_customers]
    list_of_order_ids_not_found = [None if order_id in result_ids else order_id for order_id in list_of_happy_order_ids]

    # Removing all null values and keeping only those order ids which are not found in the customer table
    list_of_order_ids_not_found = [i for i in list_of_order_ids_not_found if i]

    # This code is required as list_of_happy_order_ids might contain orderids which are not yet inserted in the customer
    # table. This code updates the happy order ids by removing the new orders which are not yet updated in the customers table
    # They will be updated when the cron runs . check cron.py
    list_of_happy_order_ids = [x for x in list_of_happy_order_ids if x not in list_of_order_ids_not_found]

    # Getting the details of the customers who have had their orders delivered in 7 days or less
    shipped_customers = Customers.objects.filter(order_id__in=list_of_happy_order_ids)

    for temp in shipped_customers:
        dict_of_order_id[temp.order_id]['first_name'] = temp.first_name
        dict_of_order_id[temp.order_id]['last_name'] = temp.last_name
        dict_of_order_id[temp.order_id]['email'] = temp.email

    # For File download
    file_type_to_download = request.GET.get('download')
    if (file_type_to_download):
        if (file_type_to_download == 'customers_data'):

            list_of_order_ids = list(dict_of_order_id.keys())
            list_of_firstname = []
            list_of_lastname = []
            list_of_email = []
            list_of_business_days = []
            list_of_invoice_date = []
            list_of_sales_channel = []

            for index in range(0, len(list_of_order_ids)):
                order_id = list_of_order_ids[index]

                list_of_firstname.append(dict_of_order_id[order_id]['first_name'])
                list_of_lastname.append(dict_of_order_id[order_id]['last_name'])
                list_of_email.append(dict_of_order_id[order_id]['email'])
                list_of_business_days.append(dict_of_order_id[order_id]['number_of_days'])
                list_of_invoice_date.append(dict_of_order_id[order_id]['invoiced_date'])
                list_of_sales_channel.append(dict_of_order_id[order_id]['sales_channel'])

            filename = "satisfied_customers"

            columns = ['orderid', 'first_name', 'last_name', 'email', 'business_days', 'invoice_date', 'sales_channel']
            df = pd.DataFrame(columns=columns)
            df['orderid'] = list_of_order_ids
            df['first_name'] = list_of_firstname
            df['last_name'] = list_of_lastname
            df['email'] = list_of_email
            df['business_days'] = list_of_business_days
            df['invoice_date'] = list_of_invoice_date
            df['sales_channel'] = list_of_sales_channel

            response = HttpResponse(content_type='text/csv')

            response['Content-Disposition'] = 'attachment; filename=' + filename + '.csv'

            df.to_csv(path_or_buf=response, index=False)
            return response

    return render(request, 'customers/customers.html', {"customers": True, "OrdersYetToSync": list_of_order_ids_not_found,
                                              "error_count": len(list_of_order_ids_not_found)})
