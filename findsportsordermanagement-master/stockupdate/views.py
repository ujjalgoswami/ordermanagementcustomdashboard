# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json
from stockupdate.models import stockupdate
from suppliers.models import Supplier_Details
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import pandas as pd
import os
import datetime
import glob
import csv

from django.http import HttpResponse
from django.http import Http404
from django.core.exceptions import PermissionDenied


def pending_stock_update_suppliers_for_today(request):
    dict_suppliers = {}
    list_of_order_ids = []
    current_date = datetime.date.today()

    supplier_details = Supplier_Details.objects.filter(stock_take_possible=True).exclude(
        last_stock_update=current_date)

    list_of_suppliers_not_been_stock_taken_today = [result.supplier_name for result
                                                    in supplier_details]

    dict_suppliers['Suppliers'] = list_of_suppliers_not_been_stock_taken_today

    return JsonResponse(dict_suppliers, json_dumps_params={'indent': 2})

@csrf_exempt
def index(request):
    if request.method == "POST":
        file_name = "NA"

        run_id = request.POST.get("run_id")
        stockupdate_objects=stockupdate.objects.get(run_id=run_id)

        supplier_name=getattr(stockupdate_objects,'supplier_name')
        date=str(getattr(stockupdate_objects, 'run_date'))

        created_on = request.POST.get('created_on')

        #Setting the name of the file!
        file_name=str(supplier_name)+'_STOCK_UPDATE_'+date+'.csv'


        dict_of_post_items = request.POST.items()
        for temp in dict_of_post_items:
            key, value = temp
            if("download_stock_update" in key):
                return getfile(file_name,date,request)
            elif("delete_stock_update" in key):
                #Mark the stockupdate as disabled and delete the file as well.
                stockupdate.objects.filter(run_id=run_id).update(disabled=True)

                # Deleting any exisitng file first , as sometimes the code doesn't overwrite existing file.
                path = 'static/datafiles/stockupdate/history/'
                for f in os.listdir(path):
                    if (f == file_name):
                        os.remove(os.path.join(path, file_name))
                        print("file deleted!",file_name)

            elif("approve_stock_update" in key):
                stockupdate.objects.filter(run_id=run_id).update(stock_update_approved=True)

                current_date = datetime.date.today()
                Supplier_Details.objects.filter(supplier_name=supplier_name).update(last_stock_update=current_date,last_stock_update_filename=file_name)
        return redirect("/stockupdate/?created_on="+created_on)



    stockupdate_objects = {}

    from django.contrib.auth.models import Permission

    permissions = Permission.objects.filter(user=request.user)
    list_of_permissions = [result.name for result in permissions]



    if ("Can view stockupdate" in list_of_permissions or "Can delete stockupdate" in list_of_permissions or "Can change stockupdate" in list_of_permissions or "Can add stockupdate" in list_of_permissions):
        Permission = True


        created_on = request.GET.get('created_on')
        if not (created_on is None):
            #A date has been selected
            date_time_obj = datetime.datetime.strptime(created_on, '%b. %d, %Y')
            stockupdate_objects = stockupdate.objects.filter(disabled=False,run_date=date_time_obj)

            supplier_details = Supplier_Details.objects.filter(stock_take_possible=True).exclude(last_stock_update=date_time_obj)

            list_of_suppliers_not_been_stock_taken_today = [result.supplier_name for result
                             in supplier_details]

            list_of_dicts = [(result.run_id,result.supplier_name,result.run_date,result.run_status,result.oos_items,result.prev_instock,result.new_instock,str(float(result.time_taken)/60)[0:5],result.comments,result.stock_update_approved,result.potential_new_products) for result in stockupdate_objects]


            return render(request, 'stockupdate/stockupdate.html',
                          {'stockupdate': True, 'Permission': Permission, "stockupdate_items": list_of_dicts,'showdates':False,'created_on':created_on,'list_of_suppliers_not_been_stock_taken_today':list_of_suppliers_not_been_stock_taken_today})
        else:
            #No date has been selected, Showing list of unique dates

            stockupdate_objects = stockupdate.objects.filter(disabled=False)

            list_of_dicts = [result.run_date for result in
                             stockupdate_objects]
            list_of_dicts = list(set(list_of_dicts))

            list_of_dicts.sort(reverse=True)

            return render(request, 'stockupdate/stockupdate.html',
                          {'stockupdate': True, 'Permission': Permission, "list_of_stock_update_created_on_dates": list_of_dicts,'showdates':True})


    else:

        Permission=False
        return render(request, 'stockupdate/stockupdate.html',
                      {'stockupdate': True, 'Permission': Permission})




@csrf_exempt
def setstockupdatestats(request):
    if request.method == "POST":
        post_request = request.body

        api_key = json.loads(post_request)['apikey']
        if (api_key == "findsportsapikey12345"):
            resp = json.loads(post_request)['stats']
            resp = resp.replace("'", "\"")
            resp = json.loads(resp)
            supplier_name = resp['supplier_name']
            run_date = resp['run_date']
            run_status = resp['run_status']
            oos_items = resp['oos_items']
            prev_instock = resp['prev_instock']
            new_instock = resp['new_instock']
            stock_update_approved = resp['stock_update_approved']
            comments = resp['comments']
            time_taken = resp['time_taken']

            supplier_name_db = Supplier_Details.objects.get(supplier_name=supplier_name)
            try:
                # Looking for existing data for today's stockupdate
                stockupdate_objects = stockupdate.objects.get(supplier_name=supplier_name_db, run_date=run_date)
                print("Stock update data for today already exists")
            except:
                # Inserting new stats

                stockupdatestats = stockupdate(
                    supplier_name=supplier_name_db,
                    run_date=run_date,
                    run_status=run_status,
                    oos_items=oos_items,
                    prev_instock=prev_instock,
                    new_instock=new_instock,
                    time_taken=time_taken,
                    stock_update_approved=stock_update_approved,
                    comments=comments
                )
                stockupdatestats.save()

            return HttpResponse("<h1>Valid Post</h1> ")

        else:
            return HttpResponse("<h1>Invalid Post</h1>")


    else:
        return HttpResponse("<h1>Invalid Post</h1>")

@csrf_exempt
def getfile(filename,date,request):
    try:
        path="https://findsportsdashboard.s3.us-east-2.amazonaws.com/StockUpdateHistory/"+str(date)+"/"+filename.replace(" ","+")
        df = pd.read_csv(path)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+filename
        df.to_csv(path_or_buf=response, index=False)
        return response
    except:
        action = request.GET.get('action', '')
        if action == 'raise403':
            raise PermissionDenied
        elif action == 'raise404':
            raise Http404
        elif action == 'raise500':
            raise Exception('Server error')

        return render(request, '500error/500error.html',
                      {'stockupdate': True})

@csrf_exempt
def bulkdownload(request):
    if request.method == "POST":
        created_on = request.POST.get('created_on')
        date_time_obj = datetime.datetime.strptime(created_on, '%b. %d, %Y')
        date=str(date_time_obj).replace(" 00:00:00","")

        stockupdate_objects = stockupdate.objects.filter(disabled=False, run_date=date_time_obj,stock_update_approved=True)
        list_of_suppliers = [getattr(result.supplier_name, 'supplier_name') for result in
                         stockupdate_objects]

        list_of_links=[]
        for single_supplier in list_of_suppliers:
            file_name=single_supplier+"_STOCK_UPDATE_"+date+".csv"
            list_of_links.append("https://findsportsdashboard.s3.us-east-2.amazonaws.com/StockUpdateHistory/"+str(date)+"/"+file_name.replace(" ","+"))

        try:
            df = pd.concat((pd.read_csv(f, header = 0) for f in list_of_links))

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=' +"StockUpdate_"+date+".csv"
            df.to_csv(path_or_buf=response, index=False)
            return response
        except:
            return redirect("/stockupdate")



# interesting_files = glob.glob("/Users/ujjalgoswami/Desktop/django/django1env/projects/findsportsordermanagement/static/datafiles/stockupdate/*.csv")
# df = pd.concat((pd.read_csv(f, header = 0) for f in interesting_files))
# df.to_csv("/Users/ujjalgoswami/Desktop/django/django1env/projects/findsportsordermanagement/static/datafiles/stockupdate/output.csv",index=False)