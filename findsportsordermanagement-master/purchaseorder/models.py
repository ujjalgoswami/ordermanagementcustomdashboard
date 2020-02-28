import uuid
from django.template.defaulttags import register
from django.db import models

# Create your models here.
from suppliers.models import Supplier_Details


class purchaseorder(models.Model):
    purchase_orderid=models.CharField(primary_key=True,max_length=100)
    supplier_name=models.ForeignKey(
        Supplier_Details, on_delete=models.CASCADE,null=True)
    created_date=models.DateField()
    tracking_id = models.CharField(max_length=100,null=True)
    courier = models.CharField(max_length=100,null=True)
    submitted = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    received_date = models.DateField(null=True)
    stock_confirmed=models.BooleanField(default=False)
    submitted_date = models.DateField(null=True)
    alias=models.CharField(max_length=100,unique=True)
    legacy_purchase_id=models.BooleanField(default=False)
    internal_notes=models.TextField(default="")

    def __str__(self):
        template = '{0.purchase_orderid} {0.tracking_id} {0.courier} {0.created_date}'
        return template.format(self)

class purchaseorder_details(models.Model):
    purchase_orderid = models.ForeignKey(
        purchaseorder, on_delete=models.CASCADE)
    sku = models.TextField()
    qty = models.TextField()
    order_line_id = models.TextField()
    instock = models.TextField()
    part_number = models.TextField()

class orderid_purchaseorderid(models.Model):
    order_id = models.CharField(max_length=100)
    sku=models.TextField(null=True)
    order_line_id=models.CharField(max_length=100)

    purchase_orderid = models.ForeignKey(
        purchaseorder, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['order_id', 'order_line_id','purchase_orderid','sku']

class sub_purchaseorder(models.Model):
    sub_purchaseorderid=models.CharField(primary_key=True,max_length=100)
    tracking_id = models.CharField(max_length=100,null=True)
    courier = models.CharField(max_length=100,null=True)
    submitted = models.BooleanField(default=False)
    stock_confirmed=models.BooleanField(default=False)
    submitted_date = models.DateField(null=True)
    alias=models.CharField(max_length=100,unique=True)
    purchase_orderid = models.ForeignKey(
        purchaseorder, on_delete=models.CASCADE)


class orderline(models.Model):
    order_line_id = models.TextField(primary_key=True)
    sku = models.TextField()
    part_number = models.TextField()
    qty = models.IntegerField()
    instock = models.IntegerField()
    dropship=models.BooleanField(default=False)
    purchase_orderid = models.ForeignKey(
        purchaseorder, on_delete=models.CASCADE)
    sub_purchaseorderid=models.ForeignKey(
        sub_purchaseorder, on_delete=models.CASCADE,null=True)
    reorder=models.BooleanField(default=False)
    available_in_store = models.BooleanField(default=False)
    refund_resolved = models.BooleanField(default=False)