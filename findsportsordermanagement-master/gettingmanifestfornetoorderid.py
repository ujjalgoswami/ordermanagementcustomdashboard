#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import datetime
from selenium import webdriver
import re
import json
from selenium.webdriver.common.keys import Keys
start = time.time()
import requests
from selenium.webdriver.chrome.options import Options


# In[ ]:


import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendemail(subject,body,receiver_email,path_to_attachment,attachment=False):
    sender_email = "findsportsnotifications@gmail.com"
    password = 'find@sports123'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    if(attachment):
        filename = path_to_attachment  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


# In[ ]:





# In[ ]:


isProduction=True

if(isProduction):
    isLogging=False
else:
    isLogging=True
    
isLogging=True
    

link='http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/automation/undispatchedorders'
link2='http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/automation/setdispathedorders'
link3='http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/automation/dispatchedorders'



r = requests.get(link)
list_of_order_id=r.json()['Orders']

if(isLogging):
    print(list_of_order_id,len(list_of_order_id))


chrome_options = Options()
chrome_options.add_argument("--headless")

list_of_manifest_numbers=[]
dict_order_id_lodged_on={}

if(isProduction):
    driver = webdriver.Chrome(chrome_options=chrome_options)
else:
    driver = webdriver.Chrome('/Users/ujjalgoswami/Downloads/chromedriver',chrome_options=chrome_options)

driver.get('https://www.findsports.com.au/_cpanel/login')




time.sleep(3)
driver.find_element_by_xpath('//*[@id="username"]').send_keys("automation")
time.sleep(3)
driver.find_element_by_xpath('//*[@id="password"]').send_keys("Automation@find321")
time.sleep(3)
driver.find_element_by_xpath("/html/body/form/div/div[3]/div/div/div[1]/div/div[3]/button").submit()
time.sleep(3)


def return_lodged_on(order_id):

    driver.get('https://www.findsports.com.au/_cpanel/order/vieworder?id='+str(order_id)+'&warehouse=y')
    time.sleep(1)

    html = str(driver.page_source)
    time.sleep(1)
    
    loop=True
    while(loop):
        if('take over this order' in str(driver.page_source).lower()):
            driver.find_element_by_link_text("Take Over This Order").click()
        else:
            loop=False


    shipping_div=driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='E-mail'])[1]/following::table[1]").get_attribute("innerHTML")
    if("4 maxwell street" in str(shipping_div)):
        no_shipping_required=True
    else:
        no_shipping_required=False
    

    
    custom_box_4=driver.find_element_by_name("_odr_cref4").get_attribute("value").lower()
    delay=False
    if(custom_box_4=="delayed" or custom_box_4=="delay" or custom_box_4=="d"):
        delay=True
    
#     if("Partially Refunded" in str(html)):
#         lodged_on="partialrefund"
    if(("Customer has elected to pickup order, shipping not required" in str(html)) or (no_shipping_required==True) or ("Shop Sale Free Pickup" in str(html))):
        lodged_on="clickncollect"
    elif("drop ship" in str(html).lower() or "dropship" in str(html).lower() or "dropshipped" in str(html).lower() or "drop shipped" in str(html).lower()):
        lodged_on="dropshipped"
        print("This item has bene dropshipped!")
    else:
        
        
        ###Figuring out if an order is late 
        ######
        
        
        manifest_number=re.findall('Manifest#\s(.*)</a></font>', html,re.IGNORECASE)
        #Checking if manifest number exists :
        if(len(manifest_number)==0):
            #Its a late order. Manifest not created
            lodged_on="Not Lodged"
        else:
            #Manifest exists
            #TODO: Check if Manifest is submitted or not
            
            #Getting the link of manifest
            
            list_of_manifest_linkID=re.findall('id=(.*)">Manifest#\s.*</a></font>', html,re.IGNORECASE)
            
            for manifest_link_id in list_of_manifest_linkID:
                m_link="https://www.findsports.com.au/_cpanel/manifest/view?id="+str(manifest_link_id)
                #Opening the manifest
                driver.get(m_link)
                time.sleep(1)
                html=str(driver.page_source)
                #Fetching the manifest submitted date
                list_of_date_submitted=re.findall('Date Submitted.*\n.*<td>(.*)<font size', html,re.IGNORECASE)
                if(len(list_of_date_submitted)>0):
                    manifest_submitted_date=list_of_date_submitted[0]
                    manifest_submitted_date=manifest_submitted_date.strip()
                    lodged_on=datetime.datetime.strptime(manifest_submitted_date, '%a, %d %b %Y').strftime('%Y-%m-%d')
                else:
                    lodged_on="Not Lodged"
                    #If any one of the manifests of that order id is not logged then stop there and mark it as not logged!
                    break
                
        
    
    ########
    
    
    if(delay):
        return [lodged_on,True]
    else:
        return lodged_on
    


if not("It looks like you are still logged in somewhere" in driver.page_source):    
    if(isLogging):
        print(len(list_of_order_id))
    
    try:
        for index in range(0,len(list_of_order_id)):

            order_id=list_of_order_id[index]
            logged_on=return_lodged_on(order_id)
            dict_order_id_lodged_on[order_id]=logged_on
            if(isLogging):
                print(index,order_id,logged_on)
    except Exception as e:
        if(isLogging):
            print(e)
        driver.get('https://www.findsports.com.au/_cpanel/logout?id=K7x7DfjJwqODelFL')
        driver.quit()
    if(isLogging):
        print(dict_order_id_lodged_on)
else:
    if(isLogging):
        print("Account still logged in!!")


# In[ ]:





# In[ ]:


print("Start Time:",start)
done = time.time()
print("End Time:",done)
elapsed = done - start
if(isLogging):
    print("Time Taken:",elapsed)

#Logout
try:
    driver.get('https://www.findsports.com.au/_cpanel/logout?id=K7x7DfjJwqODelFL')
    time.sleep(2)
    driver.quit()
except:
    if(isLogging):
        print("driver not present!")


# In[ ]:


#link2="http://127.0.0.1:8000/automation/setdispathedorders"

API_ENDPOINT = link2

from itertools import islice

def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}
        
        
for item in chunks(dict_order_id_lodged_on, 50):
    data={'apikey':'findsportsapikey12345','orders':item}
    r = requests.post(url = API_ENDPOINT,data=json.dumps(data)) 
    pastebin_url = r.text 
    if(isLogging):
        print(pastebin_url)


# In[ ]:


dict_order_id_lodged_on
count_not_logged=0
count_logged=0
temp_dict={}
for orderid in dict_order_id_lodged_on:
    if (dict_order_id_lodged_on[orderid]=='Not Lodged'):
        count_not_logged+=1
    else:
        count_logged+=1
        temp_dict[orderid]=dict_order_id_lodged_on[orderid]

if(count_logged==0):
    content = "Number of orders dispatched: "+str(count_logged)+"\n\n\n"+"Number of orders pending dispathced: "+str(count_not_logged)
else:
    content = "Number of orders dispatched: "+str(count_logged)+"\n\n\n"+str(temp_dict)+"\n\n\n"+"Number of orders pending dispathced: "+str(count_not_logged)


# In[ ]:


list_of_receiver_emails = ["ujjal@findsports.com.au"]

subject = "Orders Dispatched Status - FINDSPORTS DASHBOARD"
body = content
if(isProduction):
    path_to_attachment="/home/ubuntu/env/findsportsordermanagement/Dispatched_Pending_Orders_detailed.csv"
else:
    path_to_attachment="/Users/ujjalgoswami/Downloads/Dispatched_Pending_Orders_detailed.csv"

for receiver_email in list_of_receiver_emails:
    sendemail(subject,body,receiver_email,path_to_attachment,attachment=False)
    print("sent")

