from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
import datetime
# Create your views here.
from escalatedorders.models import escalatedorders, customer_service_users
from findsportsordermanagement.initialparameters import order_headers, product_headers, url, api_order_response, \
    api_product_response, sendemailofficial
from home.views import delayed_pending_dispatched, to_be_refunded, pending_dispatched, refunded, dispatched
from orders.models import email_history
from purchaseorder.models import orderid_purchaseorderid, purchaseorder, orderline
from suppliers.models import SupplierNew
from datetime import date
from django.contrib import messages
from findsportsordermanagement.initialparameters import sendemail

today = date.today()
today_date = today.strftime("%Y-%m-%d")
year = int(today_date.split("-")[0])
month = int(today_date.split("-")[1])
day = int(today_date.split("-")[2])
today_date = date(year, month, day)

current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@login_required
def index(request):

    order_id = request.GET.get('order_id')
    if not (order_id is None):
        order_id=order_id.strip()
        tracking_id = ""
        list_of_purchase_ids = []
        try:

            supplier=orderid_purchaseorderid.objects.filter(order_id=order_id)
            dict_orderline_id_purchase_order={}
            list_of_orderlineids=[]
            for temp in supplier:

                orderlineid=temp.order_line_id
                pid=temp.purchase_orderid
                dict_orderline_id_purchase_order[orderlineid]=pid
                list_of_orderlineids.append(orderlineid)

                list_of_purchase_ids.append(getattr(temp.purchase_orderid, 'purchase_orderid'))


            if(len(list_of_purchase_ids)>0):
                purchase_order = True


            else:
                purchase_order = False

        except:
            purchase_order = False

            list_of_purchase_ids = []

        if not (tracking_id == 'NA'):
            tracking = True
        else:
            tracking = False

        dict_input_filter = {"OrderID": order_id}
        json1_data = api_order_response(dict_input_filter, None)

        if len(json1_data['Order']) == 0:
            return redirect('/')
        else:
            dict_of_order_details = json1_data['Order'][0]

            customer_email=dict_of_order_details['Email']

            list_of_refundpending=to_be_refunded(today_date)[0]
            for index in range(0, len(list_of_refundpending)):
                list_of_refundpending[index] = list_of_refundpending[index][0]

            list_of_dispatched=dispatched()[0]
            for index in range(0, len(list_of_dispatched)):
                list_of_dispatched[index] = list_of_dispatched[index][0]



            list_of_refunded=refunded()[0]
            for index in range(0, len(list_of_refunded)):
                list_of_refunded[index] = list_of_refunded[index][0]

            listofpendingdispatched=pending_dispatched(today_date)[0]
            for index in range(0,len(listofpendingdispatched)):
                listofpendingdispatched[index]=listofpendingdispatched[index][0]

            if(order_id in listofpendingdispatched):
                messages.info(request, "Order is currently in list of pending dispatched!")
            elif(order_id in list_of_refundpending):
                messages.info(request, "Order is currently in list of refund pending!")
            elif(order_id in list_of_refunded):
                messages.info(request, "Order is currently in list of refunded!")
            elif(order_id in list_of_dispatched):
                messages.info(request, "Order is currently in list of dispatched!")
            else:
                messages.info(request, "Cannot locate order status. Contact admin!")


            #Dealing with partial orders
            list_of_orderline_dict=dict_of_order_details['OrderLine']
            list_of_found_orderlineids=[]
            list_of_orderline_ids = []
            if(len(list_of_orderline_dict)>1):
                #check if order id exists in orderline table

                for temp_orderline in list_of_orderline_dict:
                    list_of_orderline_ids.append(temp_orderline['OrderLineID'])


                orderlines = orderline.objects.filter(order_line_id__in=list_of_orderline_ids)

                list_of_found_orderlineids = [(result.order_line_id,result.sku,result.qty) for result in orderlines]
                # print(list_of_found_orderlineids)




                if(len(list_of_found_orderlineids)>1):
                    partial_order_eligible=True

                else:
                    partial_order_eligible = False


            else:
                partial_order_eligible = False

            dict_purchaseorderid_details={}
            dict_orderlineid_stock={}

            if(len(list_of_purchase_ids)>0):
                po_object=purchaseorder.objects.filter(purchase_orderid__in=list_of_purchase_ids)

                for temp in po_object:
                    pid=temp.purchase_orderid
                    alias = temp.alias
                    internal_comments=temp.internal_notes
                    tracking_id=temp.tracking_id
                    created_date = temp.created_date
                    received_date=temp.received_date

                    temp_dict={}
                    temp_dict['pid']=pid
                    temp_dict['alias'] = alias
                    temp_dict['internal_comments'] = internal_comments
                    temp_dict['tracking_id'] = tracking_id
                    temp_dict['created_date']=created_date
                    temp_dict['received_date'] = received_date

                    dict_purchaseorderid_details[pid]=temp_dict


                orderline_object=orderline.objects.filter(order_line_id__in=list_of_orderlineids)
                for temp in orderline_object:
                    orderline_id=temp.order_line_id
                    qty=temp.qty
                    stock=temp.instock
                    instore_available=temp.available_in_store
                    temp_dict={}
                    temp_dict['orderline_id']=orderline_id
                    temp_dict['qty'] = qty
                    temp_dict['stock'] = stock
                    temp_dict['instore_available'] = instore_available
                    dict_orderlineid_stock[orderline_id]=temp_dict





            # for orderline in  dict_orderline_id_purchase_order:

            #Escalated order
            internal_notes = ""
            handler = ""
            history = ""
            open = ""
            priority=""
            status=""
            zendesk=""
            assigned_to=""

            try:
                escalated_order=escalatedorders.objects.filter(order_id=order_id)

                for temp_es in escalated_order:
                    internal_notes = temp_es.internal_notes
                    handler = temp_es.handler
                    history = temp_es.history
                    open=bool(temp_es.open)
                    priority=temp_es.priority
                    status = temp_es.status
                    zendesk=temp_es.zendeskticket
                    assigned_to=getattr(temp_es.c_id,'c_id')
            except:
                    print("Couldnt retrieve the details!")
                    pass

            customer_service_users_object = customer_service_users.objects.filter(status=True)
            list_of_customer_service_reps = [result.name for result in customer_service_users_object]

            if(assigned_to!=""):
                assigned_to_object = customer_service_users.objects.get(c_id=assigned_to)
                assigned_to_name=getattr(assigned_to_object,'name')
            else:
                assigned_to_name=""


            #Getting the email history
            email_history_string=""
            emails_sent=email_history.objects.filter(order_id=order_id)

            email_history_string = ["SentTo: "+result2.to_email+"\n"+"Date: "+result2.sent_date+"\n"+"Handler: "+result2.handler+"\n"+"Message: "+result2.message+"\n" for result2 in emails_sent]

            email_history_string="\n".join(email_history_string)




            return render(request, 'orders/order.html',
                          {"assigned_to":assigned_to_name,"zendesk":zendesk,"status":status,"priority":priority,"internal_notes":internal_notes,"handler":handler,"history":history,"open":open,"dict_purchaseorderid_details":dict_purchaseorderid_details,"dict_orderlineid_stock":dict_orderlineid_stock,"orderid": order_id, "jsontemp": dict_of_order_details,
                           "purchase_order": purchase_order, "list_of_purchase_ids":list(set(list_of_purchase_ids)),'partial_order_eligible':partial_order_eligible,'list_of_found_orderlineids':list_of_found_orderlineids,'list_of_customer_service_reps':list_of_customer_service_reps,"customer_email":customer_email,"email_history_string":email_history_string})

def sendorderemail(request):
    if request.method == 'POST':


        email_from=request.POST.get("email_from")
        email_to=request.POST.get("email_to")
        email_msg=request.POST.get("email_msg")
        handler=request.POST.get("handler")
        orderid=request.POST.get("orderid")
        subject="FIND SPORTS #"+orderid+" ORDER UPDATE"


        try:
            sent_email = email_history(order_id=orderid, from_email=email_from, to_email=email_to,
                                              message=email_msg, handler=handler, sent_date=current_date)
            sent_email.save()

            sendemailofficial(subject, email_msg, email_to, '', actualfilename=None, attachment=False)

            messages.info(request, "Email Sent!")
        except:
            messages.info(request, "Unable to send email. Please contact Admin!")

        return redirect('/orders/?order_id=' + orderid)




def escalate(request):
    if request.method == 'POST':
        internalnotes=""
        handler=""
        priority=""
        escalate=""
        orderid=""
        history=""
        zendesk=""
        assigned_to=""
        dict_of_post_items = request.POST.items()
        for index, item in enumerate(dict_of_post_items):
            key,value=item
            if('internalnotes' in key):
                internalnotes=value.strip()
            elif('handler' in key):
                handler=value.strip()
            elif('priority' in key):
                priority=value.strip()
            elif('escalate' in key):
                escalate=value.strip()
            elif('orderid' in key):
                orderid=value.strip()
            elif('history' in key):
                history=value.strip()
            elif('open' in key):
                open=True
            elif('close' in key):
                open=False
            elif('zendesk' in key):
                zendesk=value.replace("#","").strip()
            elif('assignedto' in key):
                assigned_to=value.strip()


        current_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        email=customer_service_users.objects.get(name=assigned_to).email


        # Look for the exact one(No changes)
        exact_same_order_exist=False
        try:
            escalatedorder = escalatedorders.objects.filter(order_id=orderid, zendeskticket=zendesk,internal_notes=internalnotes, handler=handler,
                                                         priority=priority, status=escalate,open=open,c_id=customer_service_users.objects.get(
                                                                       name=assigned_to))
            escalated_orders = [result2.order_id for result2 in escalatedorder]
            if(len(escalated_orders)>0):
                exact_same_order_exist=True
            else:
                exact_same_order_exist = False
        except:
            exact_same_order_exist = False

        if not(exact_same_order_exist):

            if (open==True):
                history=history+"\n\n"+ str(current_date)+" # "+'Priority : '+priority+ " Type : "+escalate+"  "+'Status: Open'+" Handler: "+handler+" Assigned To: "+assigned_to+" Notes: "+internalnotes
                history=history.strip()
                resolved_date=''
            elif(open==False):
                history=history+"\n\n"+ str(current_date)+" # "+'Priority : '+priority+ " Type : "+escalate+"  "+'Status: Resolved'+" Handler: "+handler+" Assigned To: "+assigned_to+" Notes: "+internalnotes
                history = history.strip()
                resolved_date=current_date
            try:

                # Trying to look for already inserted

                escalatedorder2 = escalatedorders.objects.get(order_id=orderid)

                #Update
                escalatedorder2.internal_notes=internalnotes
                escalatedorder2.handler = handler
                escalatedorder2.priority = priority
                escalatedorder2.open=open
                escalatedorder2.zendeskticket=zendesk
                escalatedorder2.c_id=customer_service_users.objects.get(name=assigned_to)
                escalatedorder2.history = history
                escalatedorder2.resolved_date=resolved_date
                escalatedorder2.last_updated_date=current_date


                escalatedorder2.save(update_fields=['internal_notes'])
                escalatedorder2.save(update_fields=['handler'])
                escalatedorder2.save(update_fields=['priority'])
                escalatedorder2.save(update_fields=['open'])
                escalatedorder2.save(update_fields=['zendeskticket'])
                escalatedorder2.save(update_fields=['history'])
                escalatedorder2.save(update_fields=['c_id'])
                escalatedorder2.save(update_fields=['resolved_date'])
                escalatedorder2.save(update_fields=['last_updated_date'])



                if not(email==""):
                    subject = "Escalated order #" + orderid + " reassigned - Find Dashboard"
                    dashboard_link = "http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/escalatedorders/?handler=" + assigned_to
                    body = "Hi " + assigned_to + ",<br><br>An existing order has been assigned to you by " + handler + " on " + current_date + ".<br><br>Internal Comments: " + internalnotes + "<br><br>" + "<a target='_blank' href=" + dashboard_link + ">Click here to resolve this escalation !</a><br><br>Regards<br>Team FindDashboard"

                    sendemail(subject, body, email, '', actualfilename=None, attachment=False)


            except:
                #Couldn't find existing order . We will be creating it .
                escalatedorder3 = escalatedorders(order_id=orderid,internal_notes=internalnotes,handler=handler,priority=int(priority),status=escalate,open=open,history=history,zendeskticket=zendesk,c_id=customer_service_users.objects.get(
                                                                       name=assigned_to),created_date=current_date,resolved_date='')
                escalatedorder3.save()
                if not (email == ""):
                    subject="New escalated order #"+orderid+" assigned - Find Dashboard"
                    dashboard_link="http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/escalatedorders/?handler="+assigned_to
                    body="Hi "+assigned_to+",<br><br>An order has been escalated and has been assigned to you by "+handler+" on "+current_date+".<br><br>Internal Comments: "+internalnotes+"<br><br>"+"<a target='_blank' href="+dashboard_link+">Click here to resolve this escalation !</a><br><br>Regards<br>Team FindDashboard"
                    sendemail(subject, body, email, '',actualfilename=None, attachment=False)

    return redirect('/orders/?order_id='+orderid)