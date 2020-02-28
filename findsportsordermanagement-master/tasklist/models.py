from django.db import models

# Create your models here.
from escalatedorders.models import customer_service_users

class task_groups(models.Model):
    group_id=models.AutoField(primary_key=True)
    group_name = models.TextField(null=True)
    private=models.BooleanField(default=True)
    name = models.ForeignKey(
        customer_service_users, db_column='name', on_delete=models.CASCADE)
    class Meta:
        unique_together = ['group_id', 'name']

class tasklist(models.Model):
    task_id=models.AutoField(primary_key=True)
    name=models.ForeignKey(
        customer_service_users,db_column='name', on_delete=models.CASCADE)
    task_description=models.TextField(null=True)
    task_priority = models.IntegerField(null=True)
    start_date=models.DateField(null=True)
    estimated_end_date = models.DateField(null=True)
    completed_date = models.DateField(null=True)
    history=models.TextField(null=True)
    paused = models.BooleanField(default=False)
    group_id=models.ForeignKey(
        task_groups,db_column='group_id', on_delete=models.CASCADE,null=True)
    extension_taken=models.BooleanField(default=False)
    disabled=models.BooleanField(default=False)


    class Meta:
        permissions = [
            ("all_tasks_access", "Has access to all tasks"),
            ("all_regular_tasks_access", "Has access to all regular tasks"),
        ]

    def __str__(self):
        template = '{0.task_priority} {0.name} {0.task_description} {0.start_date} {0.completed_date}'
        return template.format(self)





class recurring_task(models.Model):
    task_id=models.ForeignKey(tasklist,db_column='task_id', on_delete=models.CASCADE)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    active= models.BooleanField(default=False)
    last_updated_date=models.DateField(null=True)


class recurring_task_log(models.Model):
    task_id=models.ForeignKey(tasklist,db_column='task_id', on_delete=models.CASCADE)
    name = models.ForeignKey(
        customer_service_users, db_column='name', on_delete=models.CASCADE)
    updated_date=models.DateField(null=True)
    class Meta:
        unique_together = ['task_id', 'name','updated_date']


