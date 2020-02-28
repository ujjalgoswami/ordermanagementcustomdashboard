from django.db import models

# Create your models here.
from purchaseorder.models import orderline
from purchaseorder.models import orderid_purchaseorderid


class partialorders(models.Model):
    order_line_id=models.ForeignKey(orderline, on_delete=models.CASCADE,null=True)
    created_date=models.DateField()
    internal_notes=models.TextField(default="")
    is_tracking=models.BooleanField(default=True)

class email_history(models.Model):
    order_id = models.TextField()
    from_email = models.TextField()
    to_email=models.TextField()
    message=models.TextField()
    sent_date=models.TextField()
    handler = models.TextField(default="Find Sports")