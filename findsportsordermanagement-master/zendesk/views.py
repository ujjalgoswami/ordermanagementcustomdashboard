from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
import requests
import json

# CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
headers = {
}


def getResponseAPI(url):
    response = requests.request("GET", url, headers=headers)

    response = response.text
    y = json.loads(response)

    return y


import json
import requests

import numpy as np
import pandas as pd
from datetime import date

today = date.today()
today_date = today.strftime("%Y-%m-%d")
year = int(today_date.split("-")[0])
month = int(today_date.split("-")[1])
day = int(today_date.split("-")[2])
today_date = date(year, month, day)

# CREDENTIALS HAVE BEEN REMOVED FOR SECURITY PURPOSES
headers = {
}


def getResponseAPI(url):
    response = requests.request("GET", url, headers=headers)

    response = response.text
    y = json.loads(response)

    return y


def getUnansweredTicketsResponse():
    #Unanswered Tickets
    y = getResponseAPI("https://findsports.zendesk.com/api/v2/views/active.json")
    list_of_views = y['views']
    dict_view_id_title = {}
    for index in range(0, len(list_of_views)):
        dict_view_id_title[str(list_of_views[index]['id'])] = list_of_views[index]['title']

    list_of_view_ids = list(dict_view_id_title.keys())
    string_view_ids = ','.join(list_of_view_ids)

    y = getResponseAPI("https://findsports.zendesk.com/api/v2/views/count_many.json?ids=" + string_view_ids)
    list_of_counts = y['view_counts']
    dict_view_title_count = {}
    for index in range(0, len(list_of_counts)):
        view_id = list_of_counts[index]['view_id']
        dict_view_title_count[dict_view_id_title[str(view_id)]] = list_of_counts[index]['value']

    y = getResponseAPI("https://findsports.zendesk.com/api/v2/views/72330187/tickets.json")
    return y

def my_custom_page_not_found_view(request,exception):
    return render(request,'error.html',{})
def get_dataframe_businessdays_count(y):
    list_of_ticket_link = []
    list_of_businessdays = []
    # Unanswered Tickets
    for ticket in y['tickets']:
        date = ticket['created_at'].split("T")[0]
        business_days = np.busday_count(date, today_date)
        list_of_ticket_link.append("https://findsports.zendesk.com/agent/tickets/" + str(ticket['id']))
        list_of_businessdays.append(business_days)

    columns = ['Link', 'Business Days']
    df = pd.DataFrame(columns=columns)
    df['Link'] = list_of_ticket_link
    df['Business Days'] = list_of_businessdays

    gk = df.groupby('Business Days')
    df_new = df[['Link', 'Business Days']].groupby(['Business Days']).size().reset_index(name='counts')

    return df_new



@login_required
def index(request):
    dict_view_title_count = {}
    dictionary_unanswered={}
    error = False
    try:

        y = getResponseAPI("https://findsports.zendesk.com/api/v2/views/active.json")
        list_of_views = y['views']
        dict_view_id_title = {}
        for index in range(0, len(list_of_views)):
            dict_view_id_title[str(list_of_views[index]['id'])] = list_of_views[index]['title']

        list_of_view_ids = list(dict_view_id_title.keys())
        string_view_ids = ','.join(list_of_view_ids)

        y = getResponseAPI("https://findsports.zendesk.com/api/v2/views/count_many.json?ids=" + string_view_ids)
        list_of_counts = y['view_counts']

        for index in range(0, len(list_of_counts)):
            view_id = list_of_counts[index]['view_id']
            dict_view_title_count[dict_view_id_title[str(view_id)]] = list_of_counts[index]['value']

        keys=['Tim','Facebook Chat','Recently solved tickets','Tracking']
        dict_view_title_count={key: dict_view_title_count[key] for key in dict_view_title_count if key not in keys}

        y=getUnansweredTicketsResponse()
        df_new=get_dataframe_businessdays_count(y)

        dictionary_unanswered = dict(zip(list(df_new['Business Days']), list(df_new['counts'])))

    except :

        error=True

    if(len(dict_view_title_count)==0):
        error = True

    return render(request,'zendesk/zendesk.html',{"dict_view_title_count":dict_view_title_count,"error":error,"dictionary_unanswered":dictionary_unanswered})