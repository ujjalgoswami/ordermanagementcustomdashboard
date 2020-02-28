from django.http import HttpResponse
from django.shortcuts import render, redirect
import pandas as pd
from django.contrib import messages
from findsportsordermanagement.initialparameters import api_product_response

# Create your views here.
def index(request):

    return render(request, 'categorization/categorization.html',{'categorization': True})


def categorization_file_upload(request):
    dict_product_details = {}
    list_of_size_charts = []
    context = {}
    prompt = {
        'order': 'This is a demo message error'
    }
    if request.method == 'GET':
        return render(request, "timebomb/timebomb.html", prompt)

    try:
        csv_file = request.FILES['myfile']

    except:
        return redirect('/categorization')


    if not (csv_file.name.endswith('.csv')):
        messages.error(request, "This is not a csv file")
    else:

        df = pd.read_csv(csv_file, encoding = "ISO-8859-1")
        list_of_sku = list(df['SKU*'])

        response=api_product_response({'SKU':list_of_sku},['SKU','ItemURL'], new_headers=None)['Item']

        dict_sku_product_url={}
        for temp in response:
            dict_sku_product_url[temp['SKU']]=temp['ItemURL']



    try:

        list_of_names = list(df['Name'])
        list_of_colors = list(df['variant_color_catch'])
        list_of_sizes = list(df['variant_size_catch'])
        list_of_size_charts=list(df['Image Alt 10 URL'])

        list_of_image1= list(df["Image URL (Main Image)"])
        list_of_image2= list(df["Image Alt 01 URL"])
        list_of_image3= list(df["Image Alt 02 URL"])
        list_of_image4= list(df["Image Alt 03 URL"])
        list_of_image5= list(df["Image Alt 04 URL"])

        list_of_catch_title= list(df["catchtitle"])

        list_of_catch_description= list(df["catchdescription"])

        list_of_shipping_width = list(df["Shipping Width"])
        list_of_shipping_length = list(df["Shipping Length"])
        list_of_shipping_height = list(df["Shipping Height"])
        list_of_shipping_category = list(df["Shipping Category"])
        try:
            list_of_shipping_weight=list(df['Shipping Weight'])
        except:
            list_of_shipping_weight=[""]*len(list_of_shipping_height)

        for index in range(0,len(list_of_names)):
            sku=list_of_sku[index]
            name=list_of_names[index]
            color=list_of_colors[index]
            size=list_of_sizes[index]
            size_chart=list_of_size_charts[index]
            image1 = list_of_image1[index]
            image2 = list_of_image2[index]
            image3 = list_of_image3[index]
            image4 = list_of_image4[index]
            image5 = list_of_image5[index]
            catch_title=list_of_catch_title[index]
            description=list_of_catch_description[index]

            shipping_width=list_of_shipping_width[index]
            shipping_length = list_of_shipping_length[index]
            shipping_height = list_of_shipping_height[index]
            shipping_category = list_of_shipping_category[index]
            shipping_weight=list_of_shipping_weight[index]


            if(str(size_chart)=='nan' or size_chart==None or str(size_chart)=='None'):
                is_size_chart = False
            else:
                is_size_chart=True

            if (str(image1) == 'nan' or image1 == None or str(image1) == 'None'):
                is_image1 = False
            else:
                is_image1 = True

            if (str(image2) == 'nan' or image2 == None or str(image2) == 'None'):
                is_image2 = False
            else:
                is_image2 = True

            if (str(image3) == 'nan' or image3 == None or str(image3) == 'None'):
                is_image3 = False
            else:
                is_image3 = True

            if (str(image4) == 'nan' or image4 == None or str(image4) == 'None'):
                is_image4 = False
            else:
                is_image4 = True

            if (str(image5) == 'nan' or image5 == None or str(image5) == 'None'):
                is_image5 = False
            else:
                is_image5 = True


            temp_dict={}
            temp_dict['sku'] = sku
            temp_dict['name']=name
            temp_dict['color'] = color
            temp_dict['size'] = size
            temp_dict['sizechart'] = size_chart
            temp_dict['image1'] = image1
            temp_dict['image2'] = image2
            temp_dict['image3'] = image3
            temp_dict['image4'] = image4
            temp_dict['image5'] = image5
            temp_dict['is_size_chart'] = is_size_chart

            temp_dict['is_image1'] = is_image1
            temp_dict['is_image2'] = is_image2
            temp_dict['is_image3'] = is_image3
            temp_dict['is_image4'] = is_image4
            temp_dict['is_image5'] = is_image5

            temp_dict['catch_title']=catch_title

            try:
                temp_dict['product_url']=dict_sku_product_url[sku]
            except:
                temp_dict['product_url'] = '#'

            temp_dict['description']=description

            temp_dict['shipping_width']=shipping_width
            temp_dict['shipping_length']=shipping_length
            temp_dict['shipping_height']=shipping_height
            temp_dict['shipping_weight']=shipping_weight
            temp_dict['shipping_category']=shipping_category


            try:
                temp_dict['description_count'] = len(description)
            except:
                temp_dict['description_count'] = 0
            dict_product_details[sku]=temp_dict

        return render(request, 'categorization/categorization.html',
                      {'categorization': True, 'dict_product_details': dict_product_details,'error':False})
    except Exception as e:
        print(e)

        return render(request, 'categorization/categorization.html',
                      {'categorization': True, 'error': True,'pageLink':'/stockupdate','errormsg':str(e)})


def downloadfilewithcomments(request):
    if request.method == 'POST':

        dict_sku_items={}


        for item in request.POST.items():
            key,value=item

            if not('csrfmiddlewaretoken' in key or 'download_file_with_comments' in key):
                sku = key.split(":")[0]
                print(key)

                if(sku in dict_sku_items):

                    if('ProductName' in key):
                        if('ProductName' in dict_sku_items[sku] and len(value)>0):
                            print('ujj!')
                            dict_sku_items[sku]['ProductName']=value
                    elif('Updated Description' in key):
                        if('Updated Description' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Description']=value
                    elif('Updated Colour' in key):
                        if('Updated Colour' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Colour']=value
                    elif('Comment' in key):
                        if('Comment' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Comment']=value
                    elif('catchtitle' in key):
                        if('catchtitle' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['catchtitle']=value
                    elif('Updated Size Chart' in key):
                        if('Updated Size Chart' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Size Chart']=value
                    elif('checked' in key):
                        if('checked' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['checked']=value
                    elif('Status' in key):
                        if('Status' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Status']=value

                    elif('catchdescription' in key):
                        if('catchdescription' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['catchdescription']=value


                    dict_sku_items[sku]['SKU *']=sku

                else:
                    dict_sku_items[sku]={'SKU *':'','ProductName':'','catchtitle':'','catchdescription':'','Comment':'','Updated Size Chart':'','Updated Description':'','Updated Colour':'','Status':''}
                    
                    if('ProductName' in key):
                        if('ProductName' in dict_sku_items[sku] and len(value)>0):
                            print('ujj!')
                            dict_sku_items[sku]['ProductName']=value
                    elif('Updated Description' in key):
                        if('Updated Description' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Description']=value
                    elif('Updated Colour' in key):
                        if('Updated Colour' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Colour']=value
                    elif('Comment' in key):
                        if('Comment' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Comment']=value
                    elif('catchtitle' in key):
                        if('catchtitle' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['catchtitle']=value
                    elif('Updated Size Chart' in key):
                        if('Updated Size Chart' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Updated Size Chart']=value
                    elif('checked' in key):
                        if('checked' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['checked']=value
                    elif('Status' in key):
                        if('Status' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['Status']=value

                    elif('catchdescription' in key):
                        if('catchdescription' in dict_sku_items[sku] and len(value)>0):
                            dict_sku_items[sku]['catchdescription']=value


                    dict_sku_items[sku]['SKU *']=sku

    df=pd.DataFrame.from_dict(dict_sku_items, orient='index')
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename='  + 'Products_Comments.csv'

    df.to_csv(path_or_buf=response, index=False)
    return response