from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from timebomb.models import timebomb
from django.contrib import messages
from django.http import HttpResponse
import pandas as pd
import pendulum
import os
import datetime
from django.conf import settings
from findsportsordermanagement.initialparameters import sendemail
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission

subject = "FindDashboard TimeBomb File has been created"
receiver_email = "sven@findsports.com.au"
path = settings.STATIC_ROOT + '/datafiles/test-import.csv'
path_to_attachment = path


def monday(receiver_email="ujjal@findsports.com.au",cc_email=['tim@findsports.com.au','sven@findsports.com.au']):
    timebomb_objects = timebomb.objects.filter(day="Monday", active=False)
    list_of_inactive_monday_skus = [result.sku for result in timebomb_objects]
    print(len(list_of_inactive_monday_skus))

    if (len(list_of_inactive_monday_skus) > 0):
        # This is the first time the cron is running today

        # Create file for timebomb for monday

        # Disabling all skus
        timebomb.objects.all().update(active=False)

        # Enabling only those skus which are assigned to Monday
        timebomb.objects.filter(day="Monday").update(active=True)

        # Fetching the next to next Monday Date(Note: Next monday will be tomorrow so we need the next week's date)
        next_Monday_Date = str(
            pendulum.now().next(pendulum.MONDAY).next(pendulum.MONDAY).strftime('%d/%m/%Y 12:00am'))

        # Updating dates to next Monday
        timebomb.objects.filter(day="Monday").update(promotion_expiry=next_Monday_Date)

        # Creating file for Monday
        create_csv("Monday")

        # Send email
        body = "Hi," + "\n\n" + "The Time bomb file for Monday has been created. Please note this file will be automatically imported by Neto at 1:00am on Monday"

        print(cc_email)
        sendemail(subject, body, receiver_email, path_to_attachment, 'test-import.csv',
                  attachment=True, cc=cc_email)
    else:
        print("All conditions satisfy. Current file will be used. New file will not be created!")


def thursday(receiver_email="ujjal@findsports.com.au", cc_email=['tim@findsports.com.au','sven@findsports.com.au']):
    timebomb_objects = timebomb.objects.filter(day="Thursday", active=False)
    list_of_inactive_thursday_skus = [result.sku for result in timebomb_objects]
    print(len(list_of_inactive_thursday_skus))

    if (len(list_of_inactive_thursday_skus) > 0):
        # This is the first time the cron is running today

        # Create file for timebomb for Thursday

        # Disabling all skus
        timebomb.objects.all().update(active=False)

        # Enabling only those skus which are assigned to Thursday
        timebomb.objects.filter(day="Thursday").update(active=True)

        # Fetching the next to next Thursday Date
        next_Thursday_Date = str(
            pendulum.now().next(pendulum.THURSDAY).next(pendulum.THURSDAY).strftime('%d/%m/%Y 12:00am'))

        # Updating dates to next Thursday
        timebomb.objects.filter(day="Thursday").update(promotion_expiry=next_Thursday_Date)

        # Creating file for Thursday
        create_csv("Thursday")

        # Send email
        body = "Hi," + "\n\n" + "The Time bomb file for Thursday has been created. Please note this file will be automatically imported by Neto at 1:00am on Thursday"

        print(cc_email)
        sendemail(subject, body, receiver_email, path_to_attachment, 'test-import.csv',
                  attachment=True, cc=cc_email)
    else:
        print("All conditions satisfy. Current file will be used. New file will not be created!")


def autocreatetimebombfile(forced=False,receiver_email="ujjal@findsports.com.au",cc_email=['sven@findsports.com.au','tim@findsports.com.au']):
    now = datetime.datetime.now()
    day = now.strftime("%A")
    print(day)

    if (forced):
        timebomb.objects.filter(day="Thursday").update(active=False)
        timebomb.objects.filter(day="Monday").update(active=False)
        if (day in ["Friday", "Saturday", "Sunday", "Monday"]):
            monday(receiver_email,cc_email)
        else:
            thursday(receiver_email,cc_email)

    else:
        if (day == "Friday"):
            monday(receiver_email,cc_email)

        elif (day == "Tuesday"):
            thursday(receiver_email,cc_email)

        else:
            # Disabling all skus
            timebomb.objects.filter(day="Thursday").update(active=False)
            timebomb.objects.filter(day="Monday").update(active=False)


def timebomb_file_upload(request):
    context = {}
    prompt = {
        'order': 'This is a demo message error'
    }
    if request.method == 'GET':
        return render(request, "timebomb/timebomb.html", prompt)

    csv_file = request.FILES['myfile']
    day = request.POST.get("day")

    if not (csv_file.name.endswith('.csv')):
        messages.error(request, "This is not a csv file")
    else:

        df = pd.read_csv(csv_file)

        list_of_skus = df['SKU']
        print("Day Selected:", day)

        timebomb_objects = timebomb.objects.filter(sku__in=list_of_skus)

        list_of_existing_skus = [result.sku for result in timebomb_objects]

        # Updating data
        if (len(list_of_existing_skus) > 0):
            timebomb.objects.filter(sku__in=list_of_existing_skus).update(active=False, day=day,
                                                                          promotion_expiry="13/02/2020 12:00am")

        # Inserting data
        list_of_new_skus = list(set(list_of_skus) - set(list_of_existing_skus))
        if (len(list_of_new_skus) > 0):
            batch = []
            for sku in list_of_new_skus:
                query = timebomb(sku=sku, active=False, promotion_expiry="13/02/2020 12:00am", day=day)
                batch.append(query)
            batch_size = 50
            timebomb.objects.bulk_create(batch, batch_size)

    return redirect("/timebomb")


@login_required
def index(request):
    permissions = Permission.objects.filter(user=request.user)

    list_of_permissions = [result.name for result in permissions]

    if ("Can view timebomb" in list_of_permissions or "Can delete timebomb" in list_of_permissions or "Can change timebomb" in list_of_permissions):
        # Permitted!

        list_of_approved_days = ["Thursday", "Monday"]
        batch = []
        list_of_skus_to_update = []

        if (request.method == 'POST'):

            req = request.POST.get("force_generate")
            receiver_email = request.POST.get("receiver_email")
            print("Force generating timebomb!")
            print("Ujjio1",receiver_email)
            timebomb.objects.filter(day="Thursday").update(active=False)
            timebomb.objects.filter(day="Monday").update(active=False)
            autocreatetimebombfile(forced=True,receiver_email=receiver_email,cc_email=[""])


        return render(request, 'timebomb/timebomb.html',
                      {'timebomb': True, 'Permission': True})
    else:

        return render(request, 'timebomb/timebomb.html',
                      {'timebomb': True, 'Permission': False})


def create_csv(day):
    path = settings.STATIC_ROOT + '/datafiles/'

    # Deleting any exisitng file first , as sometimes the code doesn't overwrite existing file.
    for f in os.listdir(path):
        if (f == 'test-import.csv'):
            os.remove(os.path.join(path, 'test-import.csv'))
            print("file deleted!")

    timebomb_objects = timebomb.objects.filter(day=day, active=True)
    List_of_skus = [result.sku for result in timebomb_objects]
    List_of_expiry_date = [result.promotion_expiry for result in timebomb_objects]

    columns = ["SKU*", "Promotion Expiry Date"]
    df = pd.DataFrame(columns=columns)
    df['SKU*'] = List_of_skus
    df['Promotion Expiry Date'] = List_of_expiry_date
    response = HttpResponse(content_type='text/csv')
    path = settings.STATIC_ROOT + '/datafiles/test-import.csv'
    response['Content-Disposition'] = 'attachment; filename=' + str(path) + ''
    df.to_csv(settings.STATIC_ROOT + '/datafiles/test-import.csv', index=False)
    return response


def getfile(request):
    path = settings.STATIC_ROOT + '/datafiles/test-import.csv'
    df = pd.read_csv(path)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test-import.csv'

    df.to_csv(path_or_buf=response, index=False)
    return response
