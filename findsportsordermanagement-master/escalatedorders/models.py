from django.db import models

class customer_service_users(models.Model):
    c_id=models.AutoField(primary_key=True,auto_created=True)
    name=models.CharField(max_length=100)
    status=models.BooleanField(default=True)
    average_time=models.CharField(max_length=50,null=True)
    score=models.IntegerField(null=True)
    email=models.TextField(null=True)
    escalation_permission=models.BooleanField(default=False)
    task_permission = models.BooleanField(default=False)
    user_permission_level = models.IntegerField(default=0)

    def __str__(self):
        template = '{0.name} {0.escalation_permission} {0.task_permission}'
        return template.format(self)

class zendesk_locked_tickets(models.Model):
    zendeskticket=models.CharField(max_length=100)
    c_id = models.ForeignKey(customer_service_users, on_delete=models.CASCADE, null=True)
    locked = models.BooleanField(default=True)


class escalatedorders(models.Model):
    order_id = models.CharField(max_length=100,primary_key=True)
    internal_notes=models.TextField(null=True)
    handler=models.CharField(max_length=100)
    priority=models.IntegerField()
    status=models.CharField(max_length=20)
    open=models.BooleanField(default=False)
    history=models.TextField(null=True)
    zendeskticket=models.CharField(max_length=20,null=True)
    c_id=models.ForeignKey(customer_service_users,on_delete=models.CASCADE,null=True)
    created_date = models.CharField(max_length=50,null=True)
    resolved_date = models.CharField(max_length=50,null=True)
    last_updated_date = models.CharField(max_length=50, null=True)


class independentescalatedtickets(models.Model):
    id = models.AutoField(primary_key=True)
    internal_notes=models.TextField(null=True)
    handler=models.CharField(max_length=100)
    priority=models.IntegerField()
    status=models.CharField(max_length=20)
    open=models.BooleanField(default=False)
    zendeskticket=models.CharField(max_length=20,null=True)
    c_id=models.ForeignKey(customer_service_users,on_delete=models.CASCADE,null=True)
    created_date=models.CharField(max_length=50,null=True)
    resolved_date = models.CharField(max_length=50,null=True)



