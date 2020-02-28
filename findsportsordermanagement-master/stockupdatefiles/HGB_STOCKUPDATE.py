#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
import CONFIG_STOCKUPDATE as config_stockudpate
#!/usr/bin/env python

isProduction=config_stockudpate.isProduction

import os.path
from datetime import datetime
import sys
import numpy as np
import pandas as pd
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import NoSuchElementException
import time 
import re
from bs4 import BeautifulSoup
import requests
import json



from selenium.webdriver.chrome.options import Options

product_headers = {
    'NETOAPI_ACTION': "GetItem",
    'NETOAPI_USERNAME': "API-User-Product",
    'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
    'Accept': "application/json",
    'Content-Type': "application/javascript",
    'cache-control': "no-cache",
    'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
}

url = "https://www.findsports.com.au/do/WS/NetoAPI"
def api_product_response(dict_filter, List_of_OutputSelector=None, new_headers=None):
    parent_dict = {}
    dict_export_status = {}
    dict_filter['OutputSelector'] = List_of_OutputSelector
    dict_export_status["ExportStatus"] = "Exported"
    dict_filter["UpdateResults"] = dict_export_status
    parent_dict['Filter'] = dict_filter
    payload = json.dumps(parent_dict)

    if new_headers is None:
        header = product_headers

    response = requests.request("POST", url, data=payload, headers=header)

    json1_data = json.loads(response.text)

    return json1_data



start = time.time()




error_found=True
max_count=0
while(error_found==True and max_count<=1):
    try:

        currentDay = datetime.now().day
        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        start = time.time()


        chrome_options = Options()
        chrome_options.add_argument("--headless")
        if(isProduction):
            driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            driver = webdriver.Chrome(config_stockudpate.downloads_folder+'chromedriver',chrome_options=chrome_options)



        driver.get("http://ebiz.landandsea.com.au/default.asp?PageNo=DEFAULT")
        time.sleep(5)
        framename = driver.find_element_by_xpath("//frame[contains(@name, 'Left')]")
        driver.switch_to.frame(framename)
        username = driver.find_element_by_id("loginout")
        password = driver.find_element_by_name("strUserPwd")

        username.send_keys("FORCE01")
        password.send_keys("2qfkrdfz")
        driver.find_element_by_id("btnOk").click()
        driver.switch_to.default_content()


        print("LOGIN SUCCESSFULL");

        time.sleep(5)

        driver.get("http://ebiz.landandsea.com.au/ProductListing.asp");


        temProductURL = list();

        list_of_HGB_SKU=api_product_response({'PrimarySupplier':'HGB'},['SKU'],None)['Item'] 

        list_of_HGB_SKU=[d['SKU'] for d in list_of_HGB_SKU]


        #Creating a list of product urls from the HGB SKUS we fetched from NETO
        for singlesku in list_of_HGB_SKU:
            temProductURL.append("http://ebiz.landandsea.com.au/product.asp?PageNo=PRODUCTCARD&Catalog=Land%20and%20Sea%20Sports%20Catalog&ProductId="+str(singlesku))


        print(len(temProductURL))



        time.sleep(10)
        priceList = list();
        availability = list();
        productSKU=list();

        for index in range(0,len(temProductURL)):
            print(index)
            row= temProductURL[index]
            driver.get(row);
            time.sleep(1)
            
            sku=list_of_HGB_SKU[index]

            #for item availability only 
            pf=driver.find_element_by_xpath("//table/tbody/tr[2]/td[1]").get_attribute("innerHTML");
            
            if('blocked' in str(pf).lower()):
                qty=0
            else:
                try:
                    m = re.search('Item Availability(.*)', str(pf))
                    qty=re.findall(r'\d+',m.group(0))[0]
                    qty=int(qty)
                except Exception as e:
                    qty=0
                    print(pf,e)
            
            productSKU.append(sku)
            availability.append(qty)


        print(len(productSKU))
        print(len(availability))

        error_found=False
    except:
        print("Error!")
        error_found=True
        max_count+=1


#Quitting the driver
driver.quit()


df = pd.DataFrame({
    'SKU':productSKU,
    'QTY':availability

});


# In[ ]:





# In[ ]:





import datetime
supplier_name="Home grown brands"

list_of_skus=list(df['SKU'])
list_of_new_qtys=list(df['QTY'])

if not(error_found):
    print("SKUS Fetched ",len(list_of_skus))

    list_of_qty_sku_dict=api_product_response({'PrimarySupplier':'HGB'},['AvailableSellQuantity','SKU','IsActive'],None)['Item']

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




link2="http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/stockupdate/setstockupdatestats"
# else:
#     link2="http://127.0.0.1:8000/stockupdate/setstockupdatestats"

API_ENDPOINT = link2



history_list_of_existing_qty = [int(i) for i in history_list_of_existing_qty] 
#Getting the number of oos products currently in Neto for this supplier

prev_in_stock=sum(i > 0 for i in history_list_of_existing_qty)



for index in range(0,len(history_list_of_new_qty)):
    if('Next Arrival Date' in str(history_list_of_new_qty[index])):
        history_list_of_new_qty[index]='0'



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

