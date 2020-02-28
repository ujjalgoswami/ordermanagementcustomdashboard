from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from escalatedorders.models import  customer_service_users
from tasklist.models import tasklist, recurring_task, task_groups, recurring_task_log
from datetime import datetime, timedelta
from django.db.models import F
from findsportsordermanagement.initialparameters import sendemail
from collections import Counter
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')


# Create your views here.
@login_required
def index(request):
    assigned_to=""
    showpending = True
    showpipeline = False
    showcompleted = False
    show_recurring_tasks = False
    list_of_grouped_tasks=[]
    recurring_tasks_lists = []
    show_grouped_tasks = False
    current_user_permission_level = customer_service_users.objects.get(c_id=customer_service_users.objects.get(
        name=request.user.first_name).c_id).user_permission_level

    customer_service_users_object = customer_service_users.objects.filter(task_permission=True).exclude(
        user_permission_level__gt=int(current_user_permission_level))

    customer_service_restricted_users_object = customer_service_users.objects.filter(task_permission=True,
                                                                                     user_permission_level__gt=int(
                                                                                         current_user_permission_level))

    list_of_restricted_users = [result.c_id for result in customer_service_restricted_users_object]

    list_of_customer_service_reps = [result.name for result in customer_service_users_object]
    date_format = "%Y-%m-%d"
    if request.method == 'GET':

        if (request.GET.get('id')):
            task_id = request.GET.get('id')
            showfilters = False
            try:
                task_list_object = tasklist.objects.get(task_id=task_id)

                task_description = task_list_object.task_description
                task_id = task_list_object.task_id
                name = task_list_object.name.__getattribute__('name')
                history = task_list_object.history
                completed_date = task_list_object.completed_date
                estimated_end_date = task_list_object.estimated_end_date
                start_date = task_list_object.start_date
                task_priority = task_list_object.task_priority
                paused = task_list_object.paused

                if (completed_date == None):
                    completed = False
                else:
                    completed = True

                try:
                    recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                        task_id=task_id))




                except:
                    recurring_task_object = {}


                #Checking if this task is assigned to a group or not!
                group_tasks_object = tasklist.objects.get(task_id=task_id)
                if(group_tasks_object.group_id==None):
                    is_group_present = False
                else:
                    is_group_present=True


                showpending = True
                showpipeline = True
                showcompleted = True



                #Showing the recurring log
                try:
                    recurring_task__log_object=recurring_task_log.objects.filter(task_id=tasklist.objects.get(
                        task_id=task_id))

                    # list_of_customer_service_reps = [(result.name,result.updated_date) for result in recurring_task__log_object]
                    log_string=""
                    list_of_logs=[]
                    for single_log in recurring_task__log_object:
                        list_of_logs.append(str(getattr(single_log.name,'name'))+" : "+str(single_log.updated_date))

                    log_string='\n'.join(
                        list_of_logs)
                except Exception as e:
                    print("Error!",e)
                    recurring_task__log_object={}


                return render(request, 'tasklist/task.html',
                              {'tasklist': True, "task_description": task_description, 'task_id': task_id,
                               'name': name, 'history': history, 'completed_date': completed_date,
                               'estimated_end_date': estimated_end_date, 'start_date': start_date,
                               'task_priority': task_priority,
                               'list_of_customer_service_reps': list_of_customer_service_reps, 'paused': paused,
                               'recurring_task_object': recurring_task_object, 'completed': completed,'is_group_present':is_group_present,'current_date':str(current_date).split(" ")[0],'recurring_task__log_object':log_string})
            except:
                # No task found!
                return redirect('/tasklist')


        elif (request.GET.get('assigned_to')):
            # User has selected a specific user, displaying all incomplete tasks for that user
            assigned_to = request.GET.get('assigned_to')

            pending_tasks_objects = tasklist.objects.filter(completed_date__isnull=True, paused=False,
                                                            name=customer_service_users.objects.get(
                                                                name=assigned_to),group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)
            paused_tasks_objects = tasklist.objects.filter(completed_date__isnull=True, paused=True,
                                                           name=customer_service_users.objects.get(
                                                               name=assigned_to),group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)
            completed_tasks_objects = tasklist.objects.filter(completed_date__isnull=False,completed_date__lte=datetime.today(), completed_date__gt=datetime.today()-timedelta(days=7),
                                                              name=customer_service_users.objects.get(
                                                                  name=assigned_to),group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)

            # Getting all recurring tasks for the current user
            current_user = request.user.first_name

            now = datetime.now()
            day = now.strftime("%A")




            if(day=='Monday'):

                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    monday=True)
            elif(day=='Tuesday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    tuesday=True)
            elif(day=='Wednesday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    wednesday=True)
            elif(day=='Thursday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    thursday=True)
            elif(day=='Friday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    friday=True)
            elif(day=='Saturday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    saturday=True)
            elif(day=='Sunday'):
                recurring_task_current_user_objects = recurring_task.objects.filter(active=True,
                                                                                    task_id__in=tasklist.objects.filter(
                                                                                        name=customer_service_users.objects.get(
                                                                                            name=current_user)),
                                                                                    sunday=True)

            print("Current Day is:",day)
            print("Current Date:",str(current_date).split(" ")[0],str(current_date.date()))

            for result in recurring_task_current_user_objects:

                if(result.last_updated_date==None or result.last_updated_date<current_date.date()):
                    recurring_tasks_lists.append((getattr(result.task_id,'task_id'), getattr(result.task_id, 'task_description'),
                                                  result.last_updated_date))
            if(len(recurring_tasks_lists)>0):
                show_recurring_tasks=True


            # Getting all groups as well

            list_of_current_user_groups = task_groups.objects.filter(name=customer_service_users.objects.get(
                name=current_user))

            list_of_current_user_groups = [result.group_id for result in list_of_current_user_groups]

            group_tasks_objects = tasklist.objects.filter(group_id__in=list_of_current_user_groups)

            for result in group_tasks_objects:
                list_of_grouped_tasks.append((result.task_id, result.task_priority, getattr(result.name, 'name'),
                                              result.task_description,
                                              (datetime.strptime(str(result.estimated_end_date),
                                                                 date_format) - datetime.strptime(
                                                  str(current_date.date()), date_format)).days, result.paused,
                                              result.estimated_end_date,getattr(result.group_id,'group_name')))

            if(len(list_of_grouped_tasks)>0):
                show_grouped_tasks=True
            else:
                show_grouped_tasks = False

            showpending = True
            showpipeline = True
            showcompleted = True
            showfilters=False



        else:
            showfilters = True
            pending_tasks_objects = tasklist.objects.filter(completed_date__isnull=True, paused=False,group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)
            paused_tasks_objects = tasklist.objects.filter(completed_date__isnull=True, paused=True,group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)
            completed_tasks_objects = tasklist.objects.filter(completed_date__isnull=False,group_id__isnull=True).exclude(
                name__in=list_of_restricted_users)



        list_of_pending_tasks = [(result.task_id, result.task_priority, getattr(result.name, 'name'),
                                  result.task_description, (datetime.strptime(str(result.estimated_end_date),
                                                                              date_format) - datetime.strptime(
            str(current_date.date()), date_format)).days, result.paused, result.estimated_end_date,result.extension_taken) for result in
                                 pending_tasks_objects]

        # making sure that if the task is over due, only then the days should dispaly value
        for index in range(0, len(list_of_pending_tasks)):
            taskid, priority, name, desc, days, paused, estimated_end_date,extension = list_of_pending_tasks[index]
            if(extension):
                list_of_pending_tasks[index] = (
                    taskid, int(priority), name, desc, 'Extended', paused, estimated_end_date, extension)
            else:
                if (int(days) >= 0):
                    list_of_pending_tasks[index] = (
                        taskid, int(priority), name, desc, 'On Track', paused, estimated_end_date,extension)

        # Handling Paused Tasks

        list_of_paused_tasks = [(result.task_id, result.task_priority, getattr(result.name, 'name'),
                                 result.task_description, (datetime.strptime(str(result.start_date),
                                                                             date_format) - datetime.strptime(
            str(current_date.date()), date_format)).days, result.paused) for result in paused_tasks_objects]

        # Handling Completed Tasks

        list_of_completed_tasks = [(result.task_id, result.task_priority, getattr(result.name, 'name'),
                                    result.task_description, (datetime.strptime(str(result.start_date),
                                                                                date_format) - datetime.strptime(
            str(current_date.date()), date_format)).days, result.paused) for result in completed_tasks_objects]

        if (len(pending_tasks_objects) > 0 or len(list_of_paused_tasks) > 0):
            showtasks = True
        else:
            showtasks = False

        list_of_pending_tasks = sorted(list_of_pending_tasks, key=lambda x: (x[1], x[2]), reverse=True)
        list_of_pending_tasks = sorted(list_of_pending_tasks, key=lambda x: (x[1], x[2]), reverse=True)

        list_of_paused_tasks = sorted(list_of_paused_tasks, key=lambda x: (x[1], x[2]), reverse=True)

        list_of_completed_tasks = sorted(list_of_completed_tasks, key=lambda x: (x[1], x[2]), reverse=True)

        list_of_grouped_tasks=sorted(list_of_grouped_tasks, key=lambda x: (x[7], x[1]), reverse=True)

        task_groups_object = task_groups.objects.filter(name=customer_service_users.objects.get(
            name=request.user.first_name))
        list_of_available_task_groups = [result.group_name for result in task_groups_object]

        if (len(list_of_available_task_groups) == 0):
            showgroups = False
        else:
            showgroups = True


        list_of_names=[]
        for temp in list_of_pending_tasks:
            task_id, task_priority, name,task_description, days, paused, estimated_end_date,extended=temp
            list_of_names.append(name)

        counter = Counter(list_of_names)
        customer_service_users_with_pending_task_count_dict = {}


        for cus_rep in list_of_customer_service_reps:
            if(cus_rep in counter):
                customer_service_users_with_pending_task_count_dict[cus_rep] = counter[cus_rep]
            else:
                customer_service_users_with_pending_task_count_dict[cus_rep] = 0



        if(request.GET.get('type')):


            task_type = request.GET.get('type')
            if(task_type=='ONGOING'):
                showpending = True
                showpipeline = False
                showcompleted = False
            elif(task_type=='PIPELINE'):
                showpending=False
                showpipeline = True
                showcompleted = False
            elif (task_type == 'COMPLETED'):
                showpending=False
                showpipeline = False
                showcompleted = True




        return render(request, 'tasklist/tasklist.html',
                      {'tasklist': True,"showfilters":showfilters,"assigned_to":assigned_to, "list_of_customer_service_reps": list_of_customer_service_reps,'show_recurring_tasks':show_recurring_tasks,
                       'pending_tasks_objects': list_of_pending_tasks, 'showtasks': showtasks,'showpending':showpending,'showpipeline':showpipeline,'showcompleted':showcompleted,'recurring_tasks_lists': recurring_tasks_lists,
                       'list_of_paused_tasks': list_of_paused_tasks,
                       'list_of_completed_tasks': list_of_completed_tasks,
                       'list_of_available_task_groups': list_of_available_task_groups, 'showgroups': showgroups,'list_of_grouped_tasks':list_of_grouped_tasks,'show_grouped_tasks':show_grouped_tasks,'customer_service_users_with_pending_task_count_dict':customer_service_users_with_pending_task_count_dict})

def recurring_task_completed(request):
    if request.method == 'POST':
        task_id=request.POST.get('task_id')
        assigned_to=request.POST.get('assigned_to')

        task_object = recurring_task.objects.get(task_id=tasklist.objects.get(task_id=task_id))
        task_object.last_updated_date = current_date
        task_object.save(update_fields=['last_updated_date'])

        recurring_task_log_object = recurring_task_log(name=customer_service_users.objects.get(
            name=request.user.first_name), task_id=tasklist.objects.get(task_id=task_id),
            updated_date=current_date)

        recurring_task_log_object.save()


    return redirect('/tasklist?assigned_to='+assigned_to)

def updatetask(request):
    if request.method == 'POST':
        task_description = request.POST.get("task_description")
        priority = request.POST.get("priority")
        assignedto = request.POST.get("assignedto")
        estimated_end_date=request.POST.get("estimated_end_date")
        task_id = request.POST.get("task_id")
        list_of_recurring_days = request.POST.getlist("recurring")
        task_submit_type = request.POST.get("task_submit_type")
        # print(request.POST)
        if (task_submit_type == 'Update'):

            task_object = tasklist.objects.get(task_id=task_id)

            prev_history = task_object.history

            if (len(list_of_recurring_days) > 0):
                new_history = str(
                    current_date) + " # " + 'Priority : ' + priority + "  " + " Assigned To: " + assignedto + " Recurring: " + ','.join(
                    list_of_recurring_days) + " Task: " + task_description
            else:
                new_history = str(
                    current_date) + " # " + 'Priority : ' + priority + "  " + " Assigned To: " + assignedto + " Task: " + task_description

            if not (prev_history == new_history):
                # Checking if the user has changed any value
                history = prev_history + "\n\n" + new_history
                task_object.task_description = task_description
                task_object.history = history
                task_object.task_priority = priority

                print(task_object.estimated_end_date,estimated_end_date)
                if not(estimated_end_date==task_object.estimated_end_date or estimated_end_date==''):
                    print('Date changed!')
                    task_object.extension_taken=True
                    task_object.estimated_end_date=estimated_end_date
                    task_object.save(update_fields=['extension_taken'])
                    task_object.save(update_fields=['estimated_end_date'])



                task_object.save(update_fields=['task_description'])
                task_object.save(update_fields=['history'])
                task_object.save(update_fields=['task_priority'])

                #Making the task as public and assigning it to someone else
                if not(assignedto==request.user.first_name):
                    task_object.group_id=None
                    task_object.save(update_fields=['group_id'])

                task_object.name = customer_service_users.objects.get(
                    name=assignedto)
                task_object.save(update_fields=['name'])

                if (len(list_of_recurring_days) == 0):
                    # checking if recurring already exists
                    try:
                        recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                            task_id=task_id))
                        # Record found, disabling the recurring task
                        recurring_task_object.active = False
                    except:
                        # No record found, Nothing to insert
                        pass
                else:
                    # User has selected some days for this recurring task
                    # checking if recurring already exists
                    try:

                        recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                            task_id=task_id))
                        # Record found, disabling the recurring task
                        recurring_task_object.monday = False
                        recurring_task_object.tuesday = False
                        recurring_task_object.wednesday = False
                        recurring_task_object.thursday = False
                        recurring_task_object.friday = False
                        recurring_task_object.saturday = False
                        recurring_task_object.sunday = False

                        if ('Monday' in list_of_recurring_days):
                            recurring_task_object.monday = True
                        if ('Tuesday' in list_of_recurring_days):
                            recurring_task_object.tuesday = True
                        if ('Wednesday' in list_of_recurring_days):
                            recurring_task_object.wednesday = True
                        if ('Thursday' in list_of_recurring_days):
                            recurring_task_object.thursday = True
                        if ('Friday' in list_of_recurring_days):
                            recurring_task_object.friday = True
                        if ('Saturday' in list_of_recurring_days):
                            recurring_task_object.saturday = True
                        if ('Sunday' in list_of_recurring_days):
                            recurring_task_object.sunday = True

                        recurring_task_object.active = True

                        recurring_task_object.save(update_fields=['monday'])
                        recurring_task_object.save(update_fields=['tuesday'])
                        recurring_task_object.save(update_fields=['wednesday'])
                        recurring_task_object.save(update_fields=['thursday'])
                        recurring_task_object.save(update_fields=['friday'])
                        recurring_task_object.save(update_fields=['saturday'])
                        recurring_task_object.save(update_fields=['sunday'])
                        recurring_task_object.save(update_fields=['active'])
                    except:
                        # No record found, Inserting new record

                        monday = False
                        tuesday = False
                        wednesday = False
                        thursday = False
                        friday = False
                        saturday = False
                        sunday = False

                        if ('Monday' in list_of_recurring_days):
                            monday = True
                        if ('Tuesday' in list_of_recurring_days):
                            tuesday = True
                        if ('Wednesday' in list_of_recurring_days):
                            wednesday = True
                        if ('Thursday' in list_of_recurring_days):
                            thursday = True
                        if ('Friday' in list_of_recurring_days):
                            friday = True
                        if ('Saturday' in list_of_recurring_days):
                            saturday = True
                        if ('Sunday' in list_of_recurring_days):
                            sunday = True

                        recurring_task_object = recurring_task(task_id=tasklist.objects.get(
                            task_id=task_id), monday=monday, tuesday=tuesday,
                            wednesday=wednesday, thursday=thursday, friday=friday,
                            saturday=saturday, sunday=sunday, active=True)
                        recurring_task_object.save()

            # email = customer_service_users.objects.get(name=assigned_to).email
            #
            # subject = "Urgent task assigned - Find Dashboard"
            # dashboard_link = "http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/escalatedorders/?handler=" + assigned_to
            #
            # email_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # body = "Hi " + assigned_to + ",<br><br>An urgent task has been assigned to you by " + handler + " on " + email_date + ".<br><br>Internal Comments: " + internalnotes + "<br><br>" + "<a target='_blank' href=" + dashboard_link + ">Click here to view !</a><br><br>Regards<br>Team FindDashboard"
            #
            # sendemail(subject, body, email, '', actualfilename=None, attachment=False)
        elif (task_submit_type == 'Completed'):

            task_object = tasklist.objects.get(task_id=task_id)

            history = task_object.history

            history = history + "\n\n" + "Completed Date: " + str(current_date)

            task_object.completed_date = current_date
            task_object.history = history
            task_object.save(update_fields=['completed_date'])
            task_object.save(update_fields=['history'])

            try:
                recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                    task_id=task_id))
                recurring_task_object.active = False
                recurring_task_object.save(update_fields=['active'])
            except:
                # No records found in recurring table
                pass

        elif (task_submit_type == 'Push To Pipeline'):
            # Pausing Task
            task_object = tasklist.objects.get(task_id=task_id)
            history = task_object.history

            history = history + "\n\n" + "Paused Date: " + str(current_date)

            task_object.history = history
            task_object.paused = True
            task_object.save(update_fields=['paused'])
            task_object.save(update_fields=['history'])

            try:
                # Pausing all recurring tasks
                recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                    task_id=task_id))
                recurring_task_object.active = False
                recurring_task_object.save(update_fields=['active'])
            except:
                # No records found in recurring table
                pass
        elif (task_submit_type == 'Resume'):
            # Pausing Task
            task_object = tasklist.objects.get(task_id=task_id)
            history = task_object.history

            history = history + "\n\n" + "Resumed Date: " + str(current_date)

            task_object.history = history
            task_object.paused = False
            # Resetting the start date
            task_object.start_date = current_date

            task_object.save(update_fields=['paused'])
            task_object.save(update_fields=['history'])
            task_object.save(update_fields=['start_date'])

            try:
                recurring_task_object = recurring_task.objects.get(task_id=tasklist.objects.get(
                    task_id=task_id))
                recurring_task_object.active = True
                recurring_task_object.save(update_fields=['active'])
            except:
                # No records found in recurring table
                pass
        elif (task_submit_type == 'MOVE TO HIGHEST PRIORITY'):
            # Fetch all
            c_id = customer_service_users.objects.get(
                name=assignedto).c_id

            # Decrementing all priorities of this user by 1 level
            tasklist.objects.filter(name=c_id,group_id__isnull=True).update(task_priority=F('task_priority') - 1)
            # Updating all -ve priorities as 0
            tasklist.objects.filter(name=c_id, task_priority__lt=1,group_id__isnull=True).update(task_priority=1)
            # Boosting the current task to top priority
            tasklist.objects.filter(task_id=task_id).update(task_priority=5)

    return redirect('/tasklist?id=' + task_id)


def newgroup(request):
    if request.method == 'POST':
        group_name = request.POST.get("group_name")
        current_user = request.user.first_name
        task_groups_object = task_groups(group_name=group_name.strip(), private=True, name=customer_service_users.objects.get(
            name=current_user))
        task_groups_object.save()

        return redirect('/tasklist')


def newtask(request):
    if request.method == 'POST':
        task_description = request.POST.get("task_description")
        assignedfrom = request.POST.get("assignedfrom")
        priority = request.POST.get("priority")
        assignedto = request.POST.get("assignedto")
        estimated_end_date = request.POST.get("estimated_end_date")

        history = str(
            current_date) + " # " + 'Priority : ' + priority + "  " + " Assigned By: " + assignedfrom + " Assigned To: " + assignedto + " Task: " + task_description

        if not(request.POST.get("task_group")==None):
            task_group = request.POST.get("task_group")
            tasklist_object = tasklist(name=customer_service_users.objects.get(
                name=assignedto), task_description=task_description,
                task_priority=int(priority), history=history, start_date=current_date,
                estimated_end_date=estimated_end_date, group_id=task_groups.objects.get(
                    group_name=task_group))
        else:
            task_group = None
            tasklist_object = tasklist(name=customer_service_users.objects.get(
                name=assignedto), task_description=task_description,
                task_priority=int(priority), history=history, start_date=current_date,
                estimated_end_date=estimated_end_date, group_id=None)


        tasklist_object.save()

        # email = customer_service_users.objects.get(name=assigned_to).email
        #
        # subject = "Urgent task assigned - Find Dashboard"
        # dashboard_link = "http://ec2-18-189-22-237.us-east-2.compute.amazonaws.com/escalatedorders/?handler=" + assigned_to
        #
        # email_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # body = "Hi " + assigned_to + ",<br><br>An urgent task has been assigned to you by " + handler + " on " + email_date + ".<br><br>Internal Comments: " + internalnotes + "<br><br>" + "<a target='_blank' href=" + dashboard_link + ">Click here to view !</a><br><br>Regards<br>Team FindDashboard"
        #
        # sendemail(subject, body, email, '', actualfilename=None, attachment=False)

    return redirect('/tasklist')
