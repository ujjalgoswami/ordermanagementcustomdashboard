import CONFIG_STOCKUPDATE as config_stockudpate
from browsermobproxy import Server
import numpy as np
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.support.ui import WebDriverWait
import math
import re
import os.path
import sys
import requests
import os
import pandas as pd
import json
from datetime import datetime
from glob import glob
from selenium.webdriver.firefox.options import Options
global process
#!/usr/bin/env python

r = requests.get("http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/automation/stock_update_supplier_details")
dict_supplier_dashboard=dict(r.json()['Suppliers'][0]['REEF'])
print(dict_supplier_dashboard)

isProduction=config_stockudpate.isProduction
#Get the buyplanid from dashboard

# params
rootDirectory = config_stockudpate.rootDirectory
sep = config_stockudpate.sep
browser = config_stockudpate.browser
reqPause = config_stockudpate.reqPause
reqQty = config_stockudpate.reqQty
threadLimit = config_stockudpate.threadLimit

folder_date=config_stockudpate.folder_date

#Brandscope
brandscope_login=config_stockudpate.brandscope_login
id_user=config_stockudpate.id_user
id_pass=config_stockudpate.id_pass
login_email=config_stockudpate.login_email
login_password=config_stockudpate.login_password

headers2=config_stockudpate.headers2


urls = [];

list_of_supplier_names=config_stockudpate.list_of_supplier_names


#These are the suppliers from neto
netoSupplierCode=config_stockudpate.netoSupplierCode

# Define COOKIES

cookies = config_stockudpate.cookies



headers = config_stockudpate.headers


params = config_stockudpate.params

size_folder=config_stockudpate.size_folder
info_file=config_stockudpate.info_file

buyplan_url=config_stockudpate.buyplan_url


lookupMonth=config_stockudpate.lookupMonth




buyPlan_id=dict_supplier_dashboard['BuyPlanID']
supplier_name=dict_supplier_dashboard['Name']
supplier_short_code=dict_supplier_dashboard['ShortCode']
brands={}
brands['url']=dict_supplier_dashboard['URL']
brands['brand']=dict_supplier_dashboard['BrandName']

print(brands)


currentDay = datetime.now().day;
currentMonth = datetime.now().month;
currentYear = datetime.now().year;

folder_date = str(currentDay) + "_" + str(currentMonth) + "_" + str(currentYear);

now = datetime.now();


start = time.time()


#Starting up the browser and signing in brandscope
server = Server(browser)
server.start()
proxy = server.create_proxy()


options = Options()
#Make headless = False if you want to open the browser for automation
options.headless = True

profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())



driver = webdriver.Firefox(options=options,firefox_profile=profile)


driver.get(brandscope_login)


username = driver.find_element_by_id(id_user)
password = driver.find_element_by_id(id_pass);
username.send_keys(login_email);
password.send_keys(login_password);
driver.find_element_by_name("commit").click();


def initate_scrapping():

    

    print("Logged In");
    time.sleep(5);

    if not os.path.exists(rootDirectory + folder_date):
      os.makedirs(rootDirectory + folder_date);

    proxy.new_har('req', options={'captureHeaders': True, 'captureContent': True})

    print(">> Brand : " + brands['brand'])
    print(">> Calling Url")
    driver.get("https://brandscope.com.au/brands/" + brands['url'] + "/products")



    time.sleep(6);

    driver.execute_script("$(document).ready(function(){"
                        + "$('body,html').animate({scrollTop: 3000}, 800); "
                        + "});");

    print(">> Scrolled")

    time.sleep(5);
    _totalProducts = driver.find_element_by_xpath('//*[@id="total_products"]');
    _totalProducts = _totalProducts.text
    _totalProducts = _totalProducts.replace("(", "")
    _totalProducts = _totalProducts.replace(")", "")



    for ent in proxy.har['log']['entries']:

                  _url = ent['request']['url']
                  if ("https://brandscope.com.au/brands/" + brands['url'] + "/products?offset=20&limit=20" == _url):
                      _request = ent['request']

    print(">> Fetched")
    time.sleep(5);
    _data = list();
    for db in _request['postData']['params']:
      temp = ()

      temp = temp + (db['name'],)
      temp = temp + (db['value'],)
      _data.append(temp)

    store = _request['postData']['params'];





    print(">> Tuple Created : " + str(len(_data)))

    print(">> Creating Directory : " + rootDirectory + folder_date + sep + brands['brand'])

    if not os.path.exists(rootDirectory + folder_date + sep + brands['brand']):
      os.makedirs(rootDirectory + folder_date + sep + brands['brand'] + sep + size_folder);

    print('https://brandscope.com.au/brands/' + brands['url'] + '/products')




    response = requests.post("https://brandscope.com.au/brands/" + brands['url'] + "/products", headers=headers ,params=params, cookies=cookies, data=_data)

    time.sleep(4)

    directory = rootDirectory + folder_date + sep + brands['brand'] + sep;
    print("Got the Products")



    with open(directory + brands['brand'] + ".txt", "w") as text_file:
      text_file.write(json.dumps(response.json()))

    listOfProduct = list();

    with open(directory + brands['brand'] + ".txt") as json_file:
      db = json.load(json_file)

    print(directory + brands['brand'] + ".txt")

    byLink = driver.find_element_by_xpath('//*[@id="submit_order"]').get_attribute("href")



    for product in db['pr']:
      listOfProduct.append(int(product['id']))

    print("Total Products - JSON: " + str(len(listOfProduct)))
    print("Total Products - Brandscope : " + str(_totalProducts))
    info=[]
    temp = dict()
    temp['data'] = store
    temp['total_product'] = _totalProducts
    temp['buyPlan_id'] = buyPlan_id
    info.append(temp)
    with open(directory+info_file, 'w') as outfile:
      json.dump(str(info), outfile)
    print("\n\n");


    urls = []

    for idx, value in enumerate(listOfProduct):

      if os.path.isfile(rootDirectory + folder_date + sep + brands['brand'] + sep + size_folder + sep + str(value) + ".txt"):
          abc = 0;
      else:
          urls.append("https://brandscope.com.au/buyplans/"+buyPlan_id+"/product_releases/" + str(
              value) + "/show_sizes")



    print("FINISHED")
    return urls


def create_qty_json_files(urls):
  payload = {}


  print("Total products found!",len(urls))



  process=0;
  for index in range(0,len(urls)):
    url=urls[index]


    if not os.path.isfile(rootDirectory + folder_date + sep + brands['brand'] + sep + size_folder + sep + str(url.split("/")[6]) + ".txt"):

        response = requests.request("GET", url, headers=headers2, data = payload)

        temp_json=response.text.encode('utf8')
        temp_json=str(json.dumps(response.text))
        find = re.compile(r".*can_modify")
        temp_string=re.search(find, temp_json).group(0)
        temp_string=temp_string.replace("quantities","").replace("=","").replace("\\ncan_modify","").replace(" ","").replace("\\","")
        temp_string=temp_string+'"'
        temp_string=temp_string.strip('"')
        d = json.loads(temp_string)

        ##This is a sleep time, if brandscope is blocking the requests then put a sleep here!
        # time.sleep(config_stockudpate.reqPause)

        with open(rootDirectory + folder_date + sep + brands['brand'] + sep + size_folder + sep + str(url.split("/")[6]) + ".txt", "w") as text_file:
            text_file.write(str(d))

        # time.sleep(reqPause)


    process += 1;
    message = "Scrapped Products :" + str(process)
    sys.stdout.write("\r" + message)
    sys.stdout.flush()





def compile_all_qty_json_files():

  list_of_dataframes=[]
  _csvCompile = list();

  db = list()
  sku = list();

  list_of_dataframes=[]

  brand = brands['brand']

  qtyJson=""
  try:

      directory = rootDirectory + folder_date + sep + brand + sep
      print(directory)

      count = 0;
      for file in glob(directory + size_folder + "/*.txt"):

          with open(file) as json_file:
              data = json_file.read()
          try:
              data = data.encode('utf-8').decode('unicode_escape')

              #print(data)
              data=data.replace("'",'"')
              qtyJson = json.loads(data)

          except Exception as e:
              print("ERROR" + file)
              print(e)

          for key, value in qtyJson.items():

              for item, k in value.items():

                  if "Spelean" == brand:
                      item = "SP" + item
                  elif "Jetpilot" == brand:
                      item = "JP" + item
                  elif "Phoenix Leisure Group" == brand:
                      item = "PLG" + item

                  if item not in sku:
                      temp = dict()


                      temp['SKU'] = item
                      temp['QTY'] = 0;

                      for i in k:

                          if i[0] == lookupMonth:
                              temp['QTY'] = i[1]
                              break

                      temp['brand'] = brand
                      sku.append(item)
                      db.append(temp)

          message = "Scrapped Products :" + str(count)
          sys.stdout.write("\r" + message)
          sys.stdout.flush()

          count += 1

      df = pd.DataFrame(db);
      list_of_dataframes.append(df)


  except Exception as e:
      print(e)


  df=list_of_dataframes[0]
  return df

import datetime

def update_stock_update_dashboard(df):

    error_found=False

    

    list_of_skus=list(df['SKU'])
    list_of_new_qtys=list(df['QTY'])

    if not(error_found):
        print("SKUS Fetched ",len(list_of_skus))

        list_of_qty_sku_dict=config_stockudpate.api_product_response({'PrimarySupplier':supplier_short_code},['AvailableSellQuantity','SKU','IsActive'],None)['Item']

        print(len(list_of_qty_sku_dict))
        columns=['Active','SKU','Existing QTY','New Qty']

        df_history = pd.DataFrame(columns=columns)

        history_list_of_skus=[]
        history_list_of_existing_qty=[]
        history_list_of_new_qty=[]
        history_list_of_active=[]


        list_of_oos_skus=[]
        list_of_skus_back_in_stock=[]

        count=0
        for index in range(0,len(list_of_qty_sku_dict)):
            existing_qty=list_of_qty_sku_dict[index]['AvailableSellQuantity']
            active=list_of_qty_sku_dict[index]['IsActive']
            sku=list_of_qty_sku_dict[index]['SKU']
            try:
                new_qty=df.loc[df['SKU'] == sku]['QTY'].values[0]
            except:
                new_qty=0

            if(new_qty==0):
                list_of_oos_skus.append(sku)
            elif(int(existing_qty)<10 and new_qty==10):
                list_of_skus_back_in_stock.append(sku)

            history_list_of_skus.append(sku)
            history_list_of_existing_qty.append(existing_qty)
            history_list_of_new_qty.append(new_qty)
            history_list_of_active.append(active)



        df_history['SKU']=history_list_of_skus
        df_history['Existing QTY']=history_list_of_existing_qty
        df_history['New Qty']=history_list_of_new_qty
        df_history['Active']=history_list_of_active

        current_date = datetime.date.today()
        if(isProduction):
            #Backup
            file_name="/home/ubuntu/findsportsordermanagement/static/datafiles/stockupdate/history/"+str(supplier_name)+"_STOCK_UPDATE_"+str(current_date)+".csv"
            df_history.to_csv(file_name,index=False)
            config_stockudpate.sendfiletos3(file_name,str(supplier_name)+"_STOCK_UPDATE_"+str(current_date)+".csv")
        else:
            #Backup
            file_name="/Users/ujjalgoswami/Desktop/django/django1env/projects/findsportsordermanagement/static/datafiles/stockupdate/history/"+str(supplier_name)+"_STOCK_UPDATE_"+str(current_date)+".csv"
            df_history.to_csv(file_name,index=False)
            config_stockudpate.sendfiletos3(file_name,str(supplier_name)+"_STOCK_UPDATE_"+str(current_date)+".csv")




        
        print("Total products Back in Stock:",len(list_of_skus_back_in_stock))
        print("Potential new products found while scrapping:",len(list_of_skus)-len(list_of_qty_sku_dict))

        print("Start Time:",start)
        done = time.time()
        print("End Time:",done)
        elapsed = done - start
        print("Time Taken:",elapsed)
        final_run_status="Success"
        comments="Run Passed"
    else:
        #Something went wrong!
        final_run_status="Failed"
        comments="Run Failed"
        
        elapsed=0
        oos_items=0


    # if(isProduction):
    link2="http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/stockupdate/setstockupdatestats"
    # else:
    #     link2="http://127.0.0.1:8000/stockupdate/setstockupdatestats"

    API_ENDPOINT = link2

    history_list_of_existing_qty = [int(i) for i in history_list_of_existing_qty] 
    #Getting the number of oos products currently in Neto for this supplier

    prev_in_stock=sum(i > 0 for i in history_list_of_existing_qty)

    history_list_of_new_qty=[int(i) for i in history_list_of_new_qty] 
    #Getting the number of oos products after the stock update
    new_in_stock=sum(i > 0 for i in history_list_of_new_qty)

    if(final_run_status=="Success"):
        oos_items=len(list_of_oos_skus)
    else:
        oos_items=0
        elapsed=""

    stats_dict={
        "supplier_name":str(supplier_name),
        "run_date":str(current_date),
        "run_status": str(final_run_status),
        "oos_items":str(oos_items),
        "prev_instock":str(prev_in_stock),
        "new_instock":str(new_in_stock),
        "stock_update_approved":"False",
        "comments":str(comments),
        "time_taken":str(elapsed)[0:8]
               }       
       
    data={'apikey':'findsportsapikey12345','stats':str(stats_dict)}
    r = requests.post(url = API_ENDPOINT,data=json.dumps(data)) 
    pastebin_url = r.text 
    print(pastebin_url)


print("Initial scrapping started")
urls=initate_scrapping()
print("Initial scrapping ended")
print("Creating json qty files started")
create_qty_json_files(urls)
print("Creating json qty files ended")
print("Compiling json qty files started")
df=compile_all_qty_json_files()
print("Compiling json qty files ended")
update_stock_update_dashboard(df)
print("Stock Update Completed")

server.stop()
driver.quit()



