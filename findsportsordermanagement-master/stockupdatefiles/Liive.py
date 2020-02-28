#!/usr/bin/env python
import CONFIG_STOCKUPDATE as config_stockudpate
#!/usr/bin/env python

isProduction=config_stockudpate.isProduction


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
from selenium.webdriver.chrome.options import Options
import requests
from datetime import datetime
import os
import numpy as np
import pandas as pd


# In[61]:


cookies = {
    'ASPSESSIONIDSQTSSTTT': 'ECIKCDNCNPJIDOOBIFDNDPLB',
    'idLiiveVision2AU%5FOrders': '16241',
    'LiiveVision2AU%5FCurrencyId': '1',
    'LiiveVision2AU%5FOrdersSession': '359963269',
    'LiiveVision2AU%5FMembersAuth': 'A002230BA0A07E12A05C69A0A06B',
    'blnMobileView': 'false',
    'LiiveVision2AU%5FShoppingDescription': '36468+Item%28s%29',
    'CartItems': '36468',
    'strViewStyle': 'List',
    'IsCartPopulated': '1',
    'LiiveVision2AU%5FLastViewed': '916%2C1035%2C919%2C918%2C916%2C999%2C914%2C1000%2C999%2C984%2C985%2C1054%2C1053%2C983%2C1046%2C1043%2C1042%2C1041%2C1040%2C',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'http://sales.liivevision.com/list.asp?idWebPage=484890&CATID=64&ListOptions=Submit&strViewStyle=List&page=1&back=1',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}

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

        driver.get("http://sales.liivevision.com/loginwcs01484893/login.html")
        username=driver.find_element_by_xpath('//*[@id="body-container"]/form/table[1]/tbody/tr/td/table/tbody/tr[2]/td[2]/input')
        password=driver.find_element_by_xpath('//*[@id="body-container"]/form/table[1]/tbody/tr/td/table/tbody/tr[3]/td[2]/input')

        username.send_keys("orders@findsports.com.au")
        password.send_keys("finds3175")

        driver.find_element_by_xpath('//*[@id="body-container"]/form/table[1]/tbody/tr/td/table/tbody/tr[4]/td[2]/input[2]').click()

        page=1;

        db=list();


        while page <=4:
            print(page)
            driver.get("http://sales.liivevision.com/list.asp?idWebPage=484890&CATID=64&ListOptions=Submit&strViewStyle=List&page="+str(page)+"&back=1")

            count=1;
            trs = driver.find_elements_by_xpath("/html/body/div[2]/div/div/table/tbody/tr/td[2]/table[5]/tbody/tr/td/table/tbody/tr")

            for tr in trs:
                count+=1;
                try:
                    a=driver.find_element_by_xpath('//*[@id="body-container"]/table[5]/tbody/tr/td/table/tbody/tr['+str(count)+']/td[2]/a').get_attribute("href")

                    sku=driver.find_element_by_xpath("/html/body/div[2]/div/div/table/tbody/tr/td[2]/table[5]/tbody/tr/td/table/tbody/tr["+str(count)+"]/td[3]").get_attribute("innerHTML");
                    temp=dict();
                    temp['link']=a
                    temp['SKU']=sku
                    db.append(temp)
                except:
                    time.sleep(1)
            page+=1;

        count=0

        d=db[1]
        count+=1

        for d in db:

            count+=1
            for s in d['link'].replace("javascript:OpenProductDetails('/prod.asp?","").replace(");void(0)","").split("&"):
                if 'idWebPage' in s:
                    idWebPage=s.replace("idWebPage=","")
                if  "CATID=" not in s and "SID=" not in s and "ID=" in s:
                    ID=s.replace("ID=","")




            params = (
            ('idWebPage', idWebPage),
            ('Type', 'MiniCart'),
            ('ID', ID),
            ('SubmitType', 'UpdateCart'),
            ('strOrderType', ''),

            ('intQty', '1000'),

            )
            data=""

            response = requests.get('http://sales.liivevision.com/prod.asp', data=data,headers=headers, params=params, cookies=cookies)
            content=str(response.content)
            qty=content.split("<script> totalItems = ")[1].replace(";</script>'","")
            d["QTY"]=qty
            print(d)
            print(qty)
            time.sleep(1)
            params = (
            ('idWebPage', idWebPage),
            ('Type', 'MiniCart'),
            ('ID', ID),
            ('SubmitType', 'UpdateCart'),
            ('strOrderType', ''),

            ('intQty', '0'),

            )
            response = requests.get('http://sales.liivevision.com/prod.asp', data=data,headers=headers, params=params, cookies=cookies)

            print(response.content)
            message = "Scrapped Products :" + str(count) 
            sys.stdout.write("\r" + message)   
            sys.stdout.flush()
        
        error_found=False
    
    except:
        print("Error!")
        error_found=True
        max_count+=1


# In[62]:


df = pd.DataFrame(db)


# In[63]:


import datetime
supplier_name="Liive"

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


# In[64]:


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




