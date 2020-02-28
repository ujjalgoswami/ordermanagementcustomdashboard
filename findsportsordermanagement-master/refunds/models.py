from django.db import models

# Create your models here.


class refunds(models.Model):
    OrderLineID=models.CharField(primary_key=True,max_length=100)
    OrderID=models.CharField(max_length=100)
    Emailed=models.TextField()
    Reason=models.TextField()
    DateRequested=models.DateField()
    BillFirstName=models.TextField()
    BillLastName=models.TextField()
    PaymentMethod=models.TextField()
    AmountPaid=models.IntegerField()
    DateInvoiced=models.DateField()