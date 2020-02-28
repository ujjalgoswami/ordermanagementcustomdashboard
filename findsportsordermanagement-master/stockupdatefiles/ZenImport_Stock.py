#!/usr/bin/env python
import CONFIG_STOCKUPDATE as config_stockudpate
#!/usr/bin/env python

isProduction=config_stockudpate.isProduction

#!/usr/bin/env python
# coding: utf-8

# In[258]:


import numpy as np
import pandas as pd
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time 
import json
from selenium.webdriver.support.ui import WebDriverWait
import math
import re
import os.path
from datetime import datetime
import sys
import requests
import datetime
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

chrome_options = Options()
chrome_options.add_argument("--headless")

if(isProduction):
    driver = webdriver.Chrome(chrome_options=chrome_options)
else:
    driver = webdriver.Chrome(config_stockudpate.downloads_folder+'chromedriver',chrome_options=chrome_options)


    
error_found=True
max_count=0
while(error_found==True and max_count<=5):
    try:
        time.sleep(5)
        driver.get("https://zenport.zenimports.com.au/home.aspx");
        time.sleep(15)

        username = driver.find_element_by_xpath('//*[@id="ctl00_ctl00_cpB_Login1_UserName"]')
        password = driver.find_element_by_xpath('//*[@id="ctl00_ctl00_cpB_Login1_Password"]')

        username.send_keys("tim@force.net.au")
        password.send_keys("Tim123")

        driver.find_element_by_xpath('//*[@id="ctl00_ctl00_cpB_Login1_LoginLink"]').click();
        error_found=False
    except:
        print("Error!")
        error_found=True
        max_count+=1



# In[259]:


error_found=True
max_count=0
while(error_found==True and max_count<=5):
    try:
        time.sleep(5)
        driver.get('https://zenport.zenimports.com.au/products/product-search.aspx');
        time.sleep(5)
        driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_btnSearchKeyword"]').click();
        time.sleep(10)
        d = driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_navTop_topPageLabel"]').text;
        d = d.replace("Page ","").split("(");
        d=d[0].split(" of ");

        _maxPage = d[1];
        _page=0;

        _listOfSKU=list();
        _listOfQty=list();

        print(_maxPage)
        
        
        _maxPage = d[1];
        _page=0;

        _listOfSKU=list();
        _listOfQty=list();
        _listOfPrice=list();
        _listOfName=list();

        while _page < int(_maxPage):
            _rows = driver.find_elements_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_gv"]/table/tbody/tr');
            count = 1;
            for row in _rows:
                count +=1;
                _listOfSKU.append( row.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_gv_ctl'+str(format(count, '02'))+'_lblItemNo"]').text);
                _listOfPrice.append( row.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_gv"]/table/tbody/tr['+ str(count - 1)+']/td[5]').text);

                _listOfName.append( row.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_gv"]/table/tbody/tr['+ str(count - 1)+']/td[2]').text);
                stock = row.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_gv"]/table/tbody/tr['+ str(count - 1)+']/td[7]').text;
                if "In-stock" in stock  :
                    stock=10;
                else:
                    stock = 0;
                _listOfQty.append(stock);

            _page += 1;
            if _page != int(_maxPage):
                driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ctl00_Mcp1_cp1_prd_pnl_navTop_btnNx"]').click();
            time.sleep(7);
            print("Current Page : "+str(_page) )
            print("Count : "+str(count) )
            print("_listOfSKU : "+str(len(_listOfSKU) ))
        
        
        error_found=False
    except:
        print("Error!")
        error_found=True
        max_count+=1


# In[260]:


df = pd.DataFrame({
    'SKU':_listOfSKU,
    'QTY':_listOfQty,
    'Price':_listOfPrice,
    'Name':_listOfName

});

supplier_name="Zen"

list_of_skus=list(df['SKU'])
list_of_new_qtys=list(df['QTY'])

if not(error_found):
    print("SKUS Fetched ",len(list_of_skus))

    list_of_qty_sku_dict=api_product_response({'PrimarySupplier':supplier_name},['AvailableSellQuantity','SKU','IsActive'],None)['Item']

    print(len(list_of_qty_sku_dict))
    columns=['Active','SKU','Existing QTY','New Qty']

    df_history = pd.DataFrame(columns=columns)

    history_list_of_skus=[]
    history_list_of_existing_qty=[]
    history_list_of_new_qty=[]
    history_list_of_active=[]
    history_list_of_scrapped_descriptions=[]
    history_list_of_scrapped_price=[]


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
        try:
            history_list_of_scrapped_descriptions.append(df.loc[df['SKU'] == sku]['Name'].values[0])
        except:
            print("No Name found!",df.loc[df['SKU'] == sku])
            history_list_of_scrapped_descriptions.append("")

        try:
            history_list_of_scrapped_price.append(df.loc[df['SKU'] == sku]['Price'].values[0])
        except:
            print("No price found!",df.loc[df['SKU'] == sku])
            history_list_of_scrapped_price.append("")



    df_history['SKU']=history_list_of_skus
    df_history['Existing QTY']=history_list_of_existing_qty
    df_history['New Qty']=history_list_of_new_qty
    df_history['Active']=history_list_of_active
    df_history['ScrappedName']=history_list_of_scrapped_descriptions
    df_history['ScrappedPrice']=history_list_of_scrapped_price

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


# In[261]:


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


# In[ ]:





# In[ ]:





# In[ ]:




