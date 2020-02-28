from django.http import HttpResponse
from django.shortcuts import render
import requests
import json

headers = {
    'Authorization': "Basic Zm9yY2UxMUBmYXN0bWFpbC5mbTpQb3BweTIwMTk=",
    'User-Agent': "PostmanRuntime/7.19.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "bcf70f77-cce2-4805-bbb5-e8147d134e88,587a8142-49c1-4c6e-b5bb-34b8bd182a8d",
    'Host': "findsports.zendesk.com",
    'Accept-Encoding': "gzip, deflate",
    'Cookie': "__cfduid=d7eeb6d88c7861d58d4cfb950639b0a9b1573600495",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}
# Create your views here.


def fetchtickets(status):
    querystring={}
    url = "https://findsports.zendesk.com/api/v2/search.json"
    if(status=='open'):
        querystring={"query": "type:ticket status:open"}
    elif(status=='pending'):
        querystring={"query": "type:ticket status:pending"}
    elif(status=='solved'):
        querystring={"query": "type:ticket status:solved"}
    elif(status=='closed'):
        querystring={"query": "type:ticket status:closed"}
    elif(status=='new'):
        querystring={"query": "type:ticket status:new"}
    elif(status=='hold'):
        querystring={"query": "type:ticket status:hold"}


    response = requests.request("GET", url, headers=headers, params=querystring)
    response = response.text
    y = json.loads(response)
    tickets = {}
    tickets['contents'] = y['results']
    total_tickets = len(y['results'])
    return [tickets,total_tickets]


def index(request):

    temp_list=fetchtickets('open')
    opentickets=temp_list[0]
    total_open_tickets=temp_list[1]

    temp_list = fetchtickets('pending')
    pendingtickets = temp_list[0]
    total_pending_tickets = temp_list[1]

    temp_list = fetchtickets('solved')
    solvedtickets = temp_list[0]
    total_solved_tickets = temp_list[1]


    temp_list = fetchtickets('closed')
    closedtickets = temp_list[0]
    total_closed_tickets = temp_list[1]


    temp_list = fetchtickets('new')
    newtickets = temp_list[0]
    total_new_tickets = temp_list[1]

    temp_list = fetchtickets('hold')
    holdtickets = temp_list[0]
    total_hold_tickets = temp_list[1]


    return render(request,'zendesk/zendesk.html',{"total_open_tickets":total_open_tickets,"opentickets":opentickets,"total_pending_tickets":total_pending_tickets,"pendingtickets":pendingtickets,"closedtickets":closedtickets,"total_closed_tickets":total_closed_tickets,"solvedtickets":solvedtickets,"total_solved_tickets":total_solved_tickets,"newtickets":newtickets,"total_new_tickets":total_new_tickets,"holdtickets":holdtickets,"total_hold_tickets":total_hold_tickets })