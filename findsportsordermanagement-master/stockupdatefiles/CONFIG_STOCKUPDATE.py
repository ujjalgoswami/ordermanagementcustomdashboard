import json
import requests
import boto3
from botocore.exceptions import NoCredentialsError
import datetime
import glob
import csv
import pandas as pd




lookupMonth="2020-02-01"

ROJO_lookupMonth="2019-12-01"

isProduction=False

production_stock_update_path="/home/ubuntu/findsportsordermanagement/"

# params



sep = "/"
chrome_driver_path=""
downloads_folder='/Users/ujjalgoswami/Downloads/'

if(isProduction):
    browser = "/home/ubuntu/findsportsordermanagement/browsermob-proxy-2.1.4/bin/browsermob-proxy"
    rootDirectory = "/home/ubuntu/findsportsordermanagement/stockupdatefiles/data/"
else:
    browser = "/Users/ujjalgoswami/Downloads/browsermob-proxy-2.1.4/bin/browsermob-proxy"
    rootDirectory = "/Users/ujjalgoswami/Downloads/stockupdate/StockUpdate/data/"
    chrome_driver_path="/Users/ujjalgoswami/Downloads/chromedriver"
    
reqPause = 0
reqQty = 10
threadLimit = 10

folder_date="";

#Brandscope
brandscope_login="https://brandscope.com.au/users/sign_in"
id_user="user_email"
id_pass="user_password"
login_email="ujjal@findsports.com.au"
login_password="WDV8MB3CHQ"


list_of_supplier_names=[
"Sea To Summit",
"Find Imports",
"No Supplier",
"HydroFlask",
"LUSTY",
"ANSCO",
"Rosbert",
"Absolute",
"Caribee",
"ROJO",
"Companion Brands",
"Thule",
"Dropshipzone",
"OE (ocean earth)",
"Whiteroom (Carve)",
"Columbia",
"Cape Byron",
"Bolle",
"Qattro Sports",
"NITRO",
"ProjectDistribution",
"Spelean",
"Home grown brands",
"MARES",
"Pheonix",
"Globe",
"Ultra",
"HGB DROP",
"Burke & Wills",
"AFN",
"XTM",
"Jet Pilot",
"Zen",
"Liive"
]


#These are the suppliers from neto
netoSupplierCode=["PhoenixLeisureGroup_2",
"REEF",
"Rosbert",
"Columbia_2",
"JetPilot",
"oe_2",
"ROJO",
"Spelean",
"XTM"]


cookies = {
    '_jsuid': '2030354831',
    '_ga': 'GA1.3.150650231.1560382975',
    '_gid': 'GA1.3.190112283.1560382975',
    'heatmaps_g2g_66545695': 'no',
    '_brandscope_session': 'VTdwTHp5VzA2U1U1eDdPZzRmdUZPWDdWcEdYS3F4ZTR0Y1dHQmgzREhYRXBnZUlrbDFVTmNTMURNQy9JNlJPaXgxMzhNQmhTWGlDZjdUWElmeVJkelRXZzI5eTMzMVJlQVoxRXFreUkvRElQcjBMUjY1R2FHRGVIRllFU3N5dDNZQk1ZQVMvR2Y2a0FoZzU5MWZ1ckQ5UzY0TFFDNmNXSVlZZ0VDckZvUWgrd0hZVkNjQzRFWjUyRHQvZUVhTGJacHI2WWlKWmszZ3dFcVBqSXNXK0RBVURNVUhuOVNnOEljc2E1OEYrcjRvSTZnTkEyNGxKQUtRYTFFMUVoQTcxSFNvd1lCQllXbkluRkI1U3VJUjlmZ2c9PS0taDd2R1I3UjE1anh4V2hxY2F5TnN1QT09--7289e0c819f8ab224fdc3370a2f009d636ea5810',
    'intercom-session-q5xws4x5': 'ejJjMWY5V2tSamdsclN2RTE1YmdYa1RSUkh0RFVWd0RvS2U2ZUVEVzMyUUE5Sm5UV25qSmpSWTBJR0pxWTM5VS0tOCtMcmRmVjc0ZnZvQ0pxbTZEaVUwQT09--cb2870d75be2ce1076e7f6f162c83bcb47f5d248',
}




headers={
      'Origin': 'https://brandscope.com.au',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-CSRF-Token': 'ike1U6jwjl1xgz7Ux1/NsJmfp2gd1a8fYamqXoRSu+RHYvb0fwTA/gQmYcKbc35gxlS76kyfkmKqM3/SPXs5LA==',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://brandscope.com.au/releases/69/products',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'Keep-Alive',
}


params = (
    ('offset', '0'),
    ('limit', '50000'))

size_folder="size"
info_file="info.txt"

buyplan_url="https://brandscope.com.au/buyplans/"




product_headers = {
    'NETOAPI_ACTION': "GetItem",
    'NETOAPI_USERNAME': "API-User-Product",
    'NETOAPI_KEY': "v0fmsHHYPqfq99lFnPJ1kQbIgynkbLJq",
    'Accept': "application/json",
    'Content-Type': "application/javascript",
    'cache-control': "no-cache",
    'Postman-Token': "2473156a-3bcc-4a64-8079-04c3a395b5ea"
}

headers2 = {
  'Connection': 'keep-alive',
  'Accept': '*/*',
  'Sec-Fetch-Dest': 'empty',
  'X-CSRF-Token': '84sBxM0Qkdw4r/+w2K1st7g3tJVbzhxeBIDva6602hhYzOGiRKLq8sg5PKequMMmZM/uhjWK4+8RFrsAkuyKWw==',
  'X-Requested-With': 'XMLHttpRequest',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Referer': 'https://brandscope.com.au/brands/69/products',
  'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
  'Cookie': '_ga=GA1.3.1857352410.1575263956; _jsuid=1082737220; _gid=GA1.3.1141379700.1581304770; _first_pageview=1; _brandscope_session=YlZrbHBYWkIzRHBQNFVkdlFHSTFJd1E3eUJIc0MyMGxDU2xIS2ZrMXJrNERxQVJVMTkxWlpsRFZBNXFVdU5pZkxKcmsxOVIweFR0RGFmdkIremxYbExsTTRXMm9rTlF5Tld4SmNEeUh4NE1taFAwQm5pWlJHL2FnWWFFK0tFRmJFaVFNbHo1Y1EvQmRkeFFZSmNrdUsrNk1BQ3hob0p3dzZiS24vcGtrQ1FwUDc4MkRvbDlIM0pDNjZUM2RzeW1RZHR6OXhuTnZwT0RHdXpldDAweERIRk9vc3NtcW95aUxlcnFwMi9sb3VhUkNSVUJTT0Z4blNUcjdRTFRPd0FxckxOUFdadlFFS3czS2hGYm5CaTdocXc9PS0tbHpwZkl0NGZ1U2ZLZSs2RWJSWXVZUT09--863de807b11b455e5cab5c08b95ee86217a6c142; _gat_UA-112762540-1=1; heatmaps_g2g_66545695=no; intercom-session-q5xws4x5=Z1FoWmJzelRGQVpYVlA1eFVvaFQ3SDkvWWsreDB1dkpJNzg5VVJOblBTVFJ1cDVqT2Z6akJpRURJZ3U3U1dmMi0tSjN2bnpZSUg2VTZtM1RFaE90QXVydz09--80965aa3c9722fd52509c4bf59493ad3a0bb4b14',
  'If-None-Match': 'W/"2095a337886d37d68d11ebcfd9fbe43f"'
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



def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id='AKIAVY3JEXOWNCW426M7',
                      aws_secret_access_key='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')

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def sendfiletos3(path_to_file,name_of_file):
  current_date = str(datetime.date.today())
  s3_file_name='StockUpdateHistory/'+current_date+'/'+name_of_file
  uploaded = upload_to_aws(str(path_to_file), 'findsportsdashboard', str(s3_file_name))
  print(name_of_file+" Sent to S3")
  pass


