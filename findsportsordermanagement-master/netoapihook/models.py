from django.db import models


# Create your models here.
class OrderHistory(models.Model):
    order_id = models.CharField(max_length=100)
    order_id.primary_key=True
    Quote = models.DateField(null=True)
    New = models.DateField(null=True)
    On_Hold = models.DateField(null=True)
    New_Backorder = models.DateField(null=True)
    Backorder_Approved = models.DateField(null=True)
    Pick = models.DateField(null=True)
    Pack = models.DateField(null=True)
    Pending_Pickup = models.DateField(null=True)
    Pending_Dispatch = models.DateField(null=True)
    Dispatched = models.DateField(null=True)
    Cancelled = models.DateField(null=True)
    Uncommitted = models.DateField(null=True)
    shipped_date = models.DateField(null=True)
    invoice_date = models.DateField(null=True)
    delayed=models.BooleanField(default=False)
    sales_channel=models.CharField(max_length=100,null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_dropshipped = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now=True)