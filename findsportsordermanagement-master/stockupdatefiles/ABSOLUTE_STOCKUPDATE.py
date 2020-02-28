#!/usr/bin/env python
# coding: utf-8

# In[2]:

import CONFIG_STOCKUPDATE as config_stockudpate
import json as _json
import pandas as pd
import time
import requests

input_file_name='absolute_stock_update.json'
output_file_name='absolute.csv'
data=config_stockudpate.downloads_folder+input_file_name

j_data = _json.loads(open(data,'r',encoding='utf8').read())
json_entries=j_data['history']


# In[3]:


list_of_skus=[]
list_of_descriptions=[]
list_of_images=[]


# In[4]:


isProduction=False
start = time.time()


# In[5]:


limit=20000
max_count=0
for index in range(0,len(json_entries)):
    try:

        json_entry=json_entries[index]['response']['body']['body']
        json_entry=_json.loads(json_entry)
        if(len(json_entry)>0):
            for index2 in range(0,len(json_entry)):
                if(max_count<limit):
                    style_number=json_entry[index2]["style_number"]
                    name=json_entry[index2]['name']
                    

                    parent_sku=json_entry[index2]['__unique_key']
                    
                    
                    __pricing=json_entry[index2]['__pricing']
                    __images=json_entry[index2]['__images']
                    __inventory_cache=json_entry[index2]['__inventory_cache']
                    __sizes=json_entry[index2]['__sizes']
                    __pricing=json_entry[index2]['__pricing']
                    print(json_entry[index2],"******")

                    
                    #Setting the images
                    if(len(__images)==0):
                        #No point getting the product
                        print("no image",style_number)
                    else:
                        #Adding image
                        #Getting the total size of possible products
                        if not("pack" in str(json_entry[index2]['description']).lower()): 
                            max_count+=1
                        else:
                            print(json_entry[index2])
                        
                else:
                    break

    except:  
        pass
        
print(max_count)


# In[ ]:





# In[6]:


dict_item_properties={}
for index in range(0,len(json_entries)):
    try:

        json_entry=json_entries[index]['response']['body']['body']
        json_entry=_json.loads(json_entry)
        if(len(json_entry)>0):
            for index2 in range(0,len(json_entry)):

                style_number=json_entry[index2]["style_number"]
                if(":" in style_number):
                    style_number=style_number.split(":")[1]
                    style_number=style_number.strip()
                    
                name=json_entry[index2]['name']
            
                parent_sku=json_entry[index2]['__unique_key']
                color=json_entry[index2]['color']

                __pricing=json_entry[index2]['__pricing']
                __images=json_entry[index2]['__images']
                __inventory_cache=json_entry[index2]['__inventory_cache']
                __sizes=json_entry[index2]['__sizes']
                __pricing=json_entry[index2]['__pricing']
                description=json_entry[index2]['description']


                #Setting the images
                if(len(__images)==0):
                    #No point getting the product
                    print("no image",style_number)
                else:
                    #Adding properties

                    if not("pack" in str(description).lower()): 
                        #inventory:
                        for single_item in __inventory_cache:
                            temp_dict={}
                            temp_dict['sku']=""
                            temp_dict['color']=""
                            temp_dict['description']=""
                            temp_dict['parent_sku']=""
                            temp_dict['upc']=""
                            temp_dict['name']=""
                            temp_dict['wholesale']=""
                            temp_dict['retail']=""
                            temp_dict['qty']=single_item['quantity']
                            temp_dict['size']=""
                            temp_dict['Image_Url']=""
                            temp_dict['Image_Url_2']=""
                            dict_item_properties[single_item['sku_id']]=temp_dict
                        #upc
                        for single_size in __sizes:
    #                             print(style_number)

                            for single_price in __pricing:
                                if(single_price['__currency_code']=='AUD' and single_price['__disabled']==False):
                                    dict_item_properties[single_size['_id']]['wholesale']=single_price['__wholesale']
                                    dict_item_properties[single_size['_id']]['retail']=single_price['__retail']

                                else:
                                    if(len(__pricing)==1):
                                        print("no pricing found!")

                            if(single_size['_id'] in dict_item_properties):
                                dict_item_properties[single_size['_id']]['sku']=style_number
                                dict_item_properties[single_size['_id']]['upc']=single_size['upc_code']
                                dict_item_properties[single_size['_id']]['name']=name
                                dict_item_properties[single_size['_id']]['description']=description


                                if(color=='n/a'):
                                    dict_item_properties[single_size['_id']]['color']=''
                                    dict_item_properties[single_size['_id']]['parent_sku']=''
                                else:
                                    dict_item_properties[single_size['_id']]['color']=color
                                    dict_item_properties[single_size['_id']]['parent_sku']=parent_sku.replace(",","-").replace(" ","-")+"-P"
          

                                if(single_size['__size']=='N/A'):
                                    dict_item_properties[single_size['_id']]['size']=''
                                else:
                                    dict_item_properties[single_size['_id']]['size']=single_size['__size']


                                #Adding image
                                if(len(__images)==1):
                                    dict_item_properties[single_size['_id']]['Image_Url']="https://cdn4.nuorder.com/product/"+__images[0]+".jpg"
                                elif(len(__images)==2):
                                    dict_item_properties[single_size['_id']]['Image_Url']="https://cdn4.nuorder.com/product/"+__images[0]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[1]+".jpg"
                                elif(len(__images)==3):
                                    dict_item_properties[single_size['_id']]['Image_Url']="https://cdn4.nuorder.com/product/"+__images[0]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[1]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[2]+".jpg"
                                elif(len(__images)==4):
                                    dict_item_properties[single_size['_id']]['Image_Url']="https://cdn4.nuorder.com/product/"+__images[0]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[1]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[2]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[3]+".jpg"
                                elif(len(__images)==5):
                                    dict_item_properties[single_size['_id']]['Image_Url']="https://cdn4.nuorder.com/product/"+__images[0]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[1]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[2]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[3]+".jpg"
                                    dict_item_properties[single_size['_id']]['Image_Url_2']="https://cdn4.nuorder.com/product/"+__images[4]+".jpg"

                                #TODO: do same for all remaining images


    except:  
        pass
        

print(max_count)


# In[7]:


columns=["SKU","Part No","Active","Approved","Qty","Brand","Name","Description","Cost Price","Price A","Promotion","RRP","Image Url","Image URL_2","Image URL_3","Image URL_4","Image URL_5","Image URL_6","Image URL_7","Image URL_8","Image URL_9","Image URL_10","Parent Product SKU","Specifics","Primary Supplier","Parent Category","Weight","Width","Length","Height","Cubic","Google Shipping Column","Google Custom Label 0(Supplier Name)","Google Custom label 1(Product Category)","Generate URL Automatically","UPC","Kogan Category","Kogan Department"]

df = pd.DataFrame(columns=columns)


# In[8]:


df2=pd.DataFrame.from_dict(dict_item_properties, orient='index')


# In[9]:


df2 = df2[df2["name"] != ""]


# In[10]:


df2.head()


# In[11]:


df2.to_csv(config_stockudpate.downloads_folder+"nuorder/"+output_file_name,index=False)
print("File Generated!")


# In[12]:




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
    payload = _json.dumps(parent_dict)

    if new_headers is None:
        header = product_headers

    response = requests.request("POST", url, data=payload, headers=header)

    json1_data = _json.loads(response.text)

    return json1_data


# In[13]:


error_found=False

import datetime
supplier_name="Absolute"

list_of_skus=list(df2['sku'])
list_of_new_qtys=list(df2['qty'])

if not(error_found):
    print("SKUS Fetched ",len(list_of_skus))

    list_of_qty_sku_dict=api_product_response({'PrimarySupplier':'AbsoluteBoard','IsActive':'True'},['AvailableSellQuantity','SKU','IsActive'],None)['Item']

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
            new_qty=df2.loc[df2['sku'] == sku]['qty'].values[0]
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
        file_name="/home/ubuntu/env/findsportsordermanagement/static/datafiles/stockupdate/history/"+str(supplier_name)+"_STOCK_UPDATE_"+str(current_date)+".csv"
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
r = requests.post(url = API_ENDPOINT,data=_json.dumps(data)) 
pastebin_url = r.text 
print(pastebin_url)

