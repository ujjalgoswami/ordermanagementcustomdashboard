from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from escalatedorders.models import escalatedorders, customer_service_users, zendesk_locked_tickets, \
    independentescalatedtickets

from datetime import datetime

from findsportsordermanagement.initialparameters import sendemail

current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

current_date=datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')


# Create your views here.
@login_required
def index(request):
    List_of_escalated_orders = []
    List_of_escalated_orders2=[]
    zendesk_take_over=False

    if request.method == 'GET':
        #Handling filter by Assigned to
        escalated_orders = escalatedorders.objects.filter(open=True)
        independent_escalated_orders=independentescalatedtickets.objects.filter(open=True)
        if(request.GET.get('handler')):
            assigned_to =request.GET.get('handler')
            c_id_of_assigned_to=customer_service_users.objects.get(name=assigned_to).c_id
            escalated_orders = escalatedorders.objects.filter(open=True,c_id=customer_service_users.objects.get(c_id=c_id_of_assigned_to))

            independent_escalated_orders = independentescalatedtickets.objects.filter(open=True, c_id=customer_service_users.objects.get(
                c_id=c_id_of_assigned_to))


        elif(request.GET.get('zendesk_id')):
            zendesk_id=request.GET.get('zendesk_id').strip()
            escalated_orders = escalatedorders.objects.filter(zendeskticket=zendesk_id)

        else:
            #Handling filter by escalation type

            escalation_status = request.GET.get('escalation_status')
            if (escalation_status == "tracking"):
                # Show tracking orders
                escalated_orders = escalatedorders.objects.filter(open=True, status='tracking')
            elif (escalation_status == "refunds"):
                # Show refund orders
                escalated_orders = escalatedorders.objects.filter(open=True, status='refunds')
            elif (escalation_status == "others"):
                # Show other orders
                escalated_orders = escalatedorders.objects.filter(open=True, status='others')
            elif (escalation_status == 'resolved'):
                # Show resolved orders
                escalated_orders = escalatedorders.objects.filter(open=False)

    list_escalated_orders=[]
    for result in escalated_orders:
        #current_date=datetime.strptime(current_date, '%Y-%b-%d  %H:%M:%S')

        try:
            updated_date = datetime.strptime(result.last_updated_date, '%Y-%m-%d %H:%M:%S')
        except:
            updated_date = datetime.strptime(result.created_date, '%Y-%m-%d %H:%M:%S')
        if(result.resolved_date==None or result.resolved_date==''):
            days=current_date-updated_date
        else:
            resolved_date = datetime.strptime(result.resolved_date, '%Y-%m-%d %H:%M:%S')
            days=resolved_date-updated_date

        day, sec = days.days, days.seconds
        hours = day * 24 + sec // 3600
        days=hours


        list_escalated_orders.append((result.order_id,result.priority,result.internal_notes,result.handler,result.status,result.zendeskticket.replace("#",""),days))

    # escalated_orders = [ for result in escalated_orders]
    escalated_orders=list_escalated_orders

    list1 = list(map(list, zip(*escalated_orders)))

    if (len(list1) > 0):
        List_of_escalated_orders = zip(list1[0], list1[1], list1[2], list1[3], list1[4], list1[5], list1[6])
        List_of_escalated_orders = list(List_of_escalated_orders)

    List_of_escalated_orders = sorted(List_of_escalated_orders, key=lambda x: x[6], reverse=True)

    if(len(List_of_escalated_orders)>0):
        showorders=True
    else:
        showorders=False
        if(request.GET.get('zendesk_id')):
            zendesk_take_over=True

    customer_service_users_object=customer_service_users.objects.filter(escalation_permission=True)
    list_of_customer_service_reps = [result.name for result in customer_service_users_object]

######
    list_independent_escalated_orders = []
    for result in independent_escalated_orders:
        if (result.resolved_date == None or result.resolved_date == ''):
            days = current_date - datetime.strptime(result.created_date, '%Y-%m-%d %H:%M:%S')
        else:
            resolved_date = datetime.strptime(result.resolved_date, '%Y-%m-%d %H:%M:%S')
            days = resolved_date - result.created_date

        day, sec = days.days, days.seconds
        hours = day * 24 + sec // 3600
        days = hours


        list_independent_escalated_orders.append((result.priority,result.internal_notes,result.handler,result.status,result.zendeskticket.replace("#",""),result.id,days))

    independent_escalated_orders = list_independent_escalated_orders
    list1 = list(map(list, zip(*independent_escalated_orders)))

    if (len(list1) > 0):
        List_of_escalated_orders2 = zip(list1[0], list1[1], list1[2], list1[3], list1[4], list1[5], list1[6])
        List_of_escalated_orders2 = list(List_of_escalated_orders2)

    List_of_escalated_orders2 = sorted(List_of_escalated_orders2, key=lambda x: x[6], reverse=True)

    if(len(List_of_escalated_orders2)>0):
        showorders2=True
    else:
        showorders2=False
        if(request.GET.get('zendesk_id')):
            zendesk_take_over=True


    return render(request, 'escalatedorders/escalatedorders.html',
                  {'escalatedorders': True,"showorders2":showorders2,"List_of_escalated_orders":List_of_escalated_orders,"showorders":showorders,"list_of_customer_service_reps":list_of_customer_service_reps,"List_of_escalated_orders2":List_of_escalated_orders2})


def updateticket(request):
    independent_escalated_ticket_id=""
    if request.method == 'POST':
        dict_of_post_items = request.POST.items()
        for index, item in enumerate(dict_of_post_items):
            key,value=item
            if(key=='independent_ticket_id'):
                independent_escalated_ticket_id=value

        if not(independent_escalated_ticket_id==""):
            independentescalatedtickets.objects.filter(id=independent_escalated_ticket_id).update(open=False,resolved_date=current_date)


    return redirect('/escalatedorders')



def newticket(request):
    if request.method == 'POST':
        internalnotes=""
        handler=""
        priority=""
        escalate=""
        zendesk=""
        assigned_to=""
        dict_of_post_items = request.POST.items()
        for index, item in enumerate(dict_of_post_items):
            key, value = item
            if ('internalnotes' in key):
                internalnotes = value.strip()
            elif ('handler' in key):
                handler = value.strip()
            elif ('priority' in key):
                priority = value.strip()
            elif ('escalate' in key):
                escalate = value.strip()
            elif ('open' in key):
                open = True
            elif ('close' in key):
                open = False
            elif ('zendesk' in key):
                zendesk = value.replace("#", "").strip()
            elif ('assignedto' in key):
                assigned_to = value.strip()

        # Look for the exact one(No changes)
        exact_same_order_exist = False
        try:
            escalatedorder = independentescalatedtickets.objects.filter(zendeskticket=zendesk,
                                                            internal_notes=internalnotes, handler=handler,
                                                            priority=priority, open=open,
                                                            c_id=customer_service_users.objects.get(
                                                                name=assigned_to),created_date=current_date)
            escalated_orders = [result2.order_id for result2 in escalatedorder]
            if (len(escalated_orders) > 0):
                exact_same_order_exist = True
            else:
                exact_same_order_exist = False
        except:
            exact_same_order_exist = False

        if not (exact_same_order_exist):

            # Couldn't find existing order . We will be creating it .
            escalatedorder = independentescalatedtickets( internal_notes=internalnotes, handler=handler,
                                             priority=int(priority), status=escalate, open=open,
                                             zendeskticket=zendesk, c_id=customer_service_users.objects.get(
                    name=assigned_to),created_date=current_date)
            escalatedorder.save()

            email = customer_service_users.objects.get(name=assigned_to).email

            subject = "Urgent task assigned - Find Dashboard"
            dashboard_link = "http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/escalatedorders/?handler=" + assigned_to

            email_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            body = "Hi " + assigned_to + ",<br><br>An urgent task has been assigned to you by " + handler + " on " + email_date + ".<br><br>Internal Comments: " + internalnotes + "<br><br>" + "<a target='_blank' href=" + dashboard_link + ">Click here to view !</a><br><br>Regards<br>Team FindDashboard"

            sendemail(subject, body, email, '', actualfilename=None, attachment=False)


        return redirect('/escalatedorders')
    else:
        print("Something went wrong!")
        return HttpResponse("OK!")