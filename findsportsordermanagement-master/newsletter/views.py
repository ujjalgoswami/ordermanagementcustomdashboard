from django.shortcuts import render, redirect

from findsportsordermanagement.initialparameters import api_product_response, api_order_response
from newsletter.models import newsletter
import datetime as DT




# Create your views here.
def index(request):
    if (request.method == 'POST'):
        dict_of_post_items = request.POST.items()
        dict_alias_details = {}
        sku = ""
        width = ""
        alias=""
        height = ""
        description = ""
        product_link = ""
        image_url = ""
        price_starting_from = ""

        for temp in dict_of_post_items:
            key, value = temp
            if not ('csrfmiddlewaretoken' in key):
                alias_name = key.split(":")[0]
                dict_alias_details[alias_name] = {}

                var = key.split(":")[1]
                if (var == 'sku'):
                    sku = value
                elif (var == 'width'):
                    width = value
                elif (var == 'height'):
                    height = value
                elif (var == 'description'):
                    description = value
                elif (var == 'product_link'):
                    product_link = value
                elif (var == 'image_url'):
                    image_url = value
                elif (var == 'price_starting_from'):
                    price_starting_from = value
                elif (var == 'alias'):
                    alias = value



                dict_alias_details[alias_name]['sku'] = sku
                dict_alias_details[alias_name]['alias'] = alias
                dict_alias_details[alias_name]['width'] = width
                dict_alias_details[alias_name]['height'] = height
                dict_alias_details[alias_name]['description'] = description
                dict_alias_details[alias_name]['product_link'] = product_link
                dict_alias_details[alias_name]['image_url'] = image_url
                dict_alias_details[alias_name]['price_starting_from'] = price_starting_from



        # Updating all products
        for single_product in dict_alias_details:
            alias_name = single_product
            sku = dict_alias_details[alias_name]['sku']
            width = dict_alias_details[alias_name]['width']
            height = dict_alias_details[alias_name]['height']
            description = dict_alias_details[alias_name]['description']
            product_link = dict_alias_details[alias_name]['product_link']
            image_url = dict_alias_details[alias_name]['image_url']
            price_starting_from = dict_alias_details[alias_name]['price_starting_from']


            if(len(sku)<=0):
                sku=''
            elif(len(description)<=0):
                description=''
            elif(len(price_starting_from)<=0):
                description=''


            newsletter.objects.filter(product_alias=alias_name).update(product_sku=sku, product_width=width,
                                                                       product_height=height,
                                                                       product_description=description,
                                                                       product_link=product_link,
                                                                       product_image_link=image_url,
                                                                       product_price_starting_from=price_starting_from)
        return redirect("/newsletter")

    list_of_alias = ["product1",
                     "product2",
                     "product3",
                     "product4",
                     "product5",
                     "product6"]
    newsletter_object = newsletter.objects.filter(product_alias__in=list_of_alias)

    dict_prod_details = {}
    for temp in newsletter_object:
        temp_dict = {}
        temp_dict['alias'] = temp.product_alias
        temp_dict['sku'] = temp.product_sku
        temp_dict['height'] = temp.product_height
        temp_dict['width'] = temp.product_width
        dict_prod_details[temp.product_alias] = temp_dict

    list_of_banners = ["Banner1",
                       "Banner2",
                       "Banner4",
                       "Banner5",
                       "Banner3"]
    newsletter_object = newsletter.objects.filter(product_alias__in=list_of_banners)
    dict_featured_prod_categ_details = {}
    for temp in newsletter_object:
        temp_dict = {}
        temp_dict['alias'] = temp.product_alias
        temp_dict['description'] = temp.product_description
        temp_dict['product_link'] = temp.product_link
        temp_dict['image_url'] = temp.product_image_link
        temp_dict['price_starting_from'] = temp.product_price_starting_from

        dict_featured_prod_categ_details[temp.product_alias] = temp_dict



    newsletter_object1 = newsletter.objects.filter(product_type='featured title')
    dict_product_tiles_row = {}
    for temp1 in newsletter_object1:
        temp_dict = {}
        temp_dict['product_link'] = temp1.product_link
        temp_dict['product_image_link'] = temp1.product_image_link
        temp_dict['width'] = temp1.product_width
        temp_dict['height'] = temp1.product_height
        temp_dict['alias'] = temp1.product_alias
        dict_product_tiles_row[temp1.product_alias] = temp_dict



    return render(request, 'newsletter/newsletterconf.html', {'dict_product_tiles_row':dict_product_tiles_row,'newsletter':True,'dict_prod_details': dict_prod_details,
                                                              'dict_featured_prod_categ_details': dict_featured_prod_categ_details})


def shownewsletter(request):
    newsletter_object = newsletter.objects.all()
    list_of_skus = [result.product_sku for result in newsletter_object]

    # Removing all skus which are none(Banner images might not have skus)
    list_of_skus = [x for x in list_of_skus if x is not None]

    # Fetching sku details
    product_json = api_product_response({'SKU': list_of_skus},
                                        List_of_OutputSelector=["Name", "Images", "PriceGroups", "ProductURL",
                                                                "ItemURL"], new_headers=None)['Item']
    dict_sku_details = {}
    for prod in product_json:

        inventory_id = prod['InventoryID']
        price_groups = prod['PriceGroups']
        images = prod['Images']
        name = prod['Name']
        sku = prod['SKU']

        product_url = prod['ItemURL']
        product_url = "https://www.findsports.com.au/" + product_url

        temp_dict = {}
        temp_dict['name'] = name
        temp_dict['sku'] = sku
        temp_dict['product_url'] = product_url

        for temp_image in images:
            if (temp_image['Name'] == "Main"):
                temp_dict['image_url'] = temp_image['URL']

        for single_price_group in price_groups[0]['PriceGroup']:
            if (single_price_group['Group'] == 'A'):
                # Checking if Promotion Active
                if ('PromotionPrice' in single_price_group):
                    temp_dict['is_promotion'] = True
                    temp_dict['was_price'] = single_price_group['Price']
                    temp_dict['now_price'] = single_price_group['PromotionPrice']
                else:
                    temp_dict['is_promotion'] = False
                    temp_dict['now_price'] = single_price_group['Price']

        dict_sku_details[sku] = temp_dict

    dict_product1 = {}
    dict_product2 = {}
    dict_product3 = {}
    dict_product4 = {}
    dict_product5 = {}
    dict_product6 = {}
    dict_banner1 = {}
    dict_banner2 = {}
    dict_banner3 = {}
    dict_banner4 = {}
    dict_banner5 = {}
    for temp in newsletter_object:
        sku = temp.product_sku
        if not (temp.product_sku == None):
            dict_sku_details[sku]['height'] = temp.product_height
            dict_sku_details[sku]['width'] = temp.product_width
        elif(temp.product_type=='featured title'):
            #for tiled products, they dont have skus
            dict_sku_details[sku]['height'] = temp.product_height
            dict_sku_details[sku]['width'] = temp.product_width

        if (temp.product_alias == "product1"):
            dict_product1 = dict_sku_details[sku]
        elif (temp.product_alias == "product2"):
            dict_product2 = dict_sku_details[sku]
        elif (temp.product_alias == "product3"):
            dict_product3 = dict_sku_details[sku]
        elif (temp.product_alias == "product4"):
            dict_product4 = dict_sku_details[sku]
        elif (temp.product_alias == "product5"):
            dict_product5 = dict_sku_details[sku]
        elif (temp.product_alias == "product6"):
            dict_product6 = dict_sku_details[sku]
        elif (temp.product_alias == 'Banner1'):
            dict_banner1['image_url'] = temp.product_image_link
            dict_banner1['description'] = temp.product_description
            dict_banner1['link'] = temp.product_link
        elif (temp.product_alias == 'Banner2'):
            dict_banner2['image_url'] = temp.product_image_link
            dict_banner2['description'] = temp.product_description
            dict_banner2['link'] = temp.product_link

        if (temp.product_type == 'featured category'):

            if (temp.product_alias == 'Banner4'):
                dict_banner4['image_url'] = temp.product_image_link
                dict_banner4['description'] = temp.product_description
                dict_banner4['link'] = temp.product_link
                dict_banner4['from_price'] = temp.product_price_starting_from
            elif (temp.product_alias == 'Banner5'):
                dict_banner5['image_url'] = temp.product_image_link
                dict_banner5['description'] = temp.product_description
                dict_banner5['link'] = temp.product_link
                dict_banner5['from_price'] = temp.product_price_starting_from
            elif (temp.product_alias == 'Banner3'):
                dict_banner3['image_url'] = temp.product_image_link
                dict_banner3['description'] = temp.product_description
                dict_banner3['link'] = temp.product_link
                dict_banner3['from_price'] = temp.product_price_starting_from

    list_of_featured_titles = ["featuredtitle1",
                               "featuredtitle2",
                               "featuredtitle3"]

    newsletter_object1 = newsletter.objects.filter(product_alias__in=list_of_featured_titles)
    dict_product_tiles_row1 = {}
    for temp1 in newsletter_object1:
        temp_dict = {}
        temp_dict['product_link'] = temp1.product_link
        temp_dict['product_image_link'] = temp1.product_image_link
        temp_dict['width'] = temp1.product_width
        temp_dict['height'] = temp1.product_height
        temp_dict['alias'] = temp1.product_alias
        dict_product_tiles_row1[temp1.product_alias] = temp_dict

    index=0
    html_string_featured_title_1=''
    for temp in dict_product_tiles_row1:
        product_link=dict_product_tiles_row1[temp]['product_link']
        product_image_link = dict_product_tiles_row1[temp]['product_image_link']
        width = dict_product_tiles_row1[temp]['width']
        height = dict_product_tiles_row1[temp]['height']
        alias = dict_product_tiles_row1[temp]['alias']

        if(index==0 or index==1):
            html_string_featured_title_1=html_string_featured_title_1+'<td valign="top" width="206"><table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;font-family:sans-serif;color:#4a4a4a;text-align:left" width="100%"><tbody><tr><td style="color:#666666"><a href="'+product_link+'" style="text-decoration:none;color:#666666" target="_blank"  ><img  alt="" src="'+product_image_link+'" style="font-family:Arial;color:#346699;font-size:16px" width="'+width+'" height="'+height+'" class="CToWUd"> </a></td> </tr> <tr></tr><tr></tr></tbody></table> </td> '+'<td style="font-size:12px;line-height:12px" width="11"><p style="margin:0">. </p></td>'
        else:
            html_string_featured_title_1 = html_string_featured_title_1 + '<td valign="top" width="206"><table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;font-family:sans-serif;color:#4a4a4a;text-align:left" width="100%"><tbody><tr><td style="color:#666666"><a href="' + product_link + '" style="text-decoration:none;color:#666666" target="_blank"  ><img  alt="" src="' + product_image_link + '" style="font-family:Arial;color:#346699;font-size:16px" width="' + width + '" height="' + height + '" class="CToWUd"> </a></td> </tr> <tr></tr><tr></tr></tbody></table> </td> '

        index+=1


    list_of_featured_titles2 = ["featuredtitle4",
                                "featuredtitle5",
                                "featuredtitle6"]
    newsletter_object2 = newsletter.objects.filter(product_alias__in=list_of_featured_titles2)
    dict_product_tiles_row2 = {}
    for temp2 in newsletter_object2:
        temp_dict = {}
        temp_dict['product_link'] = temp2.product_link
        temp_dict['product_image_link'] = temp2.product_image_link
        temp_dict['width'] = temp2.product_width
        temp_dict['height'] = temp2.product_height
        temp_dict['alias'] = temp2.product_alias
        dict_product_tiles_row2[temp2.product_alias] = temp_dict


    index = 0
    html_string_featured_title_2 = ''
    for temp in dict_product_tiles_row2:
        product_link = dict_product_tiles_row2[temp]['product_link']
        product_image_link = dict_product_tiles_row2[temp]['product_image_link']
        width = dict_product_tiles_row2[temp]['width']
        height = dict_product_tiles_row2[temp]['height']
        alias = dict_product_tiles_row2[temp]['alias']

        if (index == 0 or index == 1):
            html_string_featured_title_2 = html_string_featured_title_2 + '<td valign="top" width="206"><table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;font-family:sans-serif;color:#4a4a4a;text-align:left" width="100%"><tbody><tr><td style="color:#666666"><a href="' + product_link + '" style="text-decoration:none;color:#666666" target="_blank"  ><img  alt="" src="' + product_image_link + '" style="font-family:Arial;color:#346699;font-size:16px" width="' + width + '" height="' + height + '" class="CToWUd"> </a></td> </tr> <tr></tr><tr></tr></tbody></table> </td> ' + '<td style="font-size:12px;line-height:12px" width="11"><p style="margin:0">. </p></td>'
        else:
            html_string_featured_title_2 = html_string_featured_title_2 + '<td valign="top" width="206"><table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;font-family:sans-serif;color:#4a4a4a;text-align:left" width="100%"><tbody><tr><td style="color:#666666"><a href="' + product_link + '" style="text-decoration:none;color:#666666" target="_blank"  ><img  alt="" src="' + product_image_link + '" style="font-family:Arial;color:#346699;font-size:16px" width="' + width + '" height="' + height + '" class="CToWUd"> </a></td> </tr> <tr></tr><tr></tr></tbody></table> </td> '

        index += 1


    return render(request, 'newsletter/newsletter.html',
                  {'today_date':DT.date.today(),'dict_product_tiles_row1':dict_product_tiles_row1,'dict_product_tiles_row2':dict_product_tiles_row2,'dict_banner3': dict_banner3, 'dict_banner5': dict_banner5, 'dict_banner4': dict_banner4,
                   'dict_banner2': dict_banner2, 'dict_banner1': dict_banner1, 'dict_product1': dict_product1,
                   "dict_product2": dict_product2, "dict_product3": dict_product3, "dict_product4": dict_product4,
                   "dict_product5": dict_product5, "dict_product6": dict_product6,"html_string_featured_title_1":html_string_featured_title_1,"html_string_featured_title_2":html_string_featured_title_2})



def get_recommended_products(request):

    # In[95]:
    number_of_products = 100
    Number_of_days_period = 30

    today = DT.date.today()
    week_ago = today - DT.timedelta(days=Number_of_days_period)
    date = str(week_ago) + " 00:00:00"

    list_of_orderline_dicts = api_order_response({"DatePlacedFrom": date}, ["OrderLine"], None)['Order']

    # In[96]:

    dict_sku_qty = {}

    for orderline in list_of_orderline_dicts:
        list_of_orderlines = orderline['OrderLine']

        for single_orderline in list_of_orderlines:
            qty = single_orderline['Quantity']
            sku = single_orderline['SKU']

            if (sku != '4maxwell'):
                # If we have already entered the sku in the dict then just add the qty to the existing qty
                if (sku in dict_sku_qty):
                    dict_sku_qty[sku] = int(dict_sku_qty[sku]) + int(qty)
                else:
                    # enter the new sku in the dict
                    dict_sku_qty[sku] = int(qty)

    # In[97]:

    list_of_6_most_ordered_products_in_last_7_days = sorted([(value, key) for (key, value) in dict_sku_qty.items()],
                                                            reverse=True)[0:50]

    # In[98]:

    list_of_skus = []
    for temp in list_of_6_most_ordered_products_in_last_7_days:
        qty, sku = temp
        list_of_skus.append(sku)

    # In[99]:

    list_of_products_dicts = api_product_response({"SKU": list_of_skus},
                                                  List_of_OutputSelector=["Name", "Images", "AvailableSellQuantity",
                                                                          "ItemURL"], new_headers=None)['Item']

    # In[100]:

    dict_sku_name_image = {}
    for prod in list_of_products_dicts:
        temp_dict = {}
        temp_dict['SKU'] = prod['SKU']
        temp_dict['Name'] = prod['Name']
        temp_dict['Images'] = prod['Images'][0]
        temp_dict['Qty'] = prod['AvailableSellQuantity']
        temp_dict['prod_link'] = prod['ItemURL']
        dict_sku_name_image[prod['SKU']] = temp_dict

    # In[101]:

    dict_prod_details = {}
    for prod in dict_sku_name_image:
        image_path = dict_sku_name_image[prod]
        image_path = image_path['Images']['URL']
        name = dict_sku_name_image[prod]['Name']
        sku = dict_sku_name_image[prod]['SKU']
        qty = dict_sku_name_image[prod]['Qty']
        prod_link = dict_sku_name_image[prod]['prod_link']

        if (int(qty) > 0):
            temp_dict = {}
            temp_dict['SKU'] = sku
            temp_dict['QTY'] = qty
            temp_dict['NAME'] = name
            temp_dict['IMAGE_PATH'] = image_path
            temp_dict['NETO_LINK'] = "https://www.findsports.com.au/_cpanel/products/view?sku=" + str(sku)
            temp_dict['PRODUCT_LINK'] = "https://www.findsports.com.au/" + prod_link
            dict_prod_details[sku] = temp_dict


    return render(request, 'newsletter/newsletterrecommender.html',{'newsletter':True,'dict_prod_details': dict_prod_details})

