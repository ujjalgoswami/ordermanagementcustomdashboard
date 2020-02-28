#!/usr/bin/env python
# coding: utf-8

# In[227]:


import time
import re
import json
from datetime import datetime
start = time.time()
import requests

import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# In[228]:


production=True
link='http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/automation/getnotifications'
r = requests.get(link)
list_of_order_id=r.json()


# In[ ]:





# In[ ]:





# In[229]:


def sendemail(subject,body,receiver_email,cc,path_to_attachment,attachment=False):
    sender_email = "findsportsnotifications@gmail.com"
    password = 'find@sports123'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
#     message["Cc"] = cc
    #message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "html"))
    
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
            f"attachment; filename= {'Dispatched_Pending_Orders.xlsx'}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


# In[230]:


subject="FindDashboard Summary - "+str(datetime.now().date())
# body=str(list_of_order_id)




# In[231]:


#String building
suppliers=""
temp_dict=list_of_order_id['Suppliers']
for temp in temp_dict:
    suppliers+="<li><b>"+temp+" :</b> "+temp_dict[temp]['On Hold Date']+"</li>"
suppliers="<ul>"+suppliers+"</ul>"


purchaseorderpendingsubmit=""
temp_dict=list_of_order_id['PurchaseOrderPendingSubmit']
for temp in temp_dict:
    purchaseorderpendingsubmit+="<li><b>"+temp[0]+"</b> of supplier <b>"+temp[4]+" over by <b>"+str(temp[1])+"</b> Day/s </li>"
purchaseorderpendingsubmit="<ul>"+purchaseorderpendingsubmit+"</ul>"
    
purchaseorderpendingsubmit=str(purchaseorderpendingsubmit)

purchaseorderrefunds=""
temp_dict=list_of_order_id['Purchaseorderrefunds']
for temp in temp_dict:
    purchaseorderrefunds+="<li><b>OrderID: </b>"+temp_dict[temp]['orderid']+",<b>OrderlineID: </b>"+temp_dict[temp]['order_line_id']+"</li>"
purchaseorderrefunds="<ul>"+purchaseorderrefunds+"</ul>"




# In[232]:


body="""
<div align="center">
<h1>Findsports Dashboard Summary</h1>
</div>
<div align="left">
<h2>Suppliers on Hold</h2>
"""+suppliers+"""
<h2>Refunds Pending : """+str(list_of_order_id['RefundsPending'])+"""</h2>
<h2>Pending Dispatch : """+str(list_of_order_id['DispatchPending'])+"""</h2>
<h2>Purchase orders not submitted</h2>"""+purchaseorderpendingsubmit+"""
<h2>Purchase order OOS refunds:</h2>
"""+purchaseorderrefunds+"""
<h2>Purchase order tracking id pending : """+str(len(list_of_order_id['PurchaseOrderTrackingPending']))+"""</h2>

<br><br>
PFA Late orders pending dispatch file
</div>

<div align="center">
<br><br>
<a href="http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/" target="_blank" style="padding: 8px 12px; border: 1px solid #ED2939;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #000000;text-decoration: none;font-weight:bold;display: inline-block;">
                          View Dashboard             
                      </a>
</div>

"""


# In[233]:


#receiver_email="tim@findsports.com.au"
#cc="orders@findsports.com.au,liz@findsports.com.au,sven@findsports.com.au,ujjal@findsports.com.au"
receiver_email="orders@findsports.com.au"
cc="ujjalgoswami92@gmail.com"

if(production):
    path_to_attachment="/home/ubuntu/env/findsportsordermanagement/Dispatched_Pending_Orders.xlsx"
else:
    path_to_attachment="/Users/ujjalgoswami/Desktop/django/django1env/projects/findsportsordermanagement/Dispatched_Pending_Orders.xlsx"

sendemail(subject,body,receiver_email,cc,path_to_attachment,attachment=True)


# In[ ]:





# In[ ]:




