from django.db import models

# Create your models here.
class PendingDispatchOrderIDExceptions(models.Model):
    order_id=models.CharField(max_length=100,primary_key=True)
    comments = models.TextField()
    def __str__(self):
        template = '{0.order_id}'
        return template.format(self)


class PendingRefundsOrderIDExceptions(models.Model):
    order_id=models.CharField(max_length=100,primary_key=True)
    comments = models.TextField()
    def __str__(self):
        template = '{0.order_id}'
        return template.format(self)


