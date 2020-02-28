from django.db import models
from suppliers.models import Supplier_Details

# Create your models here.
class stockupdate(models.Model):
    run_id=models.AutoField(primary_key=True)
    supplier_name=models.ForeignKey(
        Supplier_Details, on_delete=models.CASCADE)
    run_date=models.DateField()
    run_status=models.CharField(max_length=50)
    oos_items=models.IntegerField(null=True)
    prev_instock=models.IntegerField(null=True)
    new_instock = models.IntegerField(null=True)
    time_taken=models.CharField(max_length=10,null=True)
    stock_update_approved=models.BooleanField(default=False)
    comments = models.TextField(null=True)
    potential_new_products = models.IntegerField(null=True)
    disabled=models.BooleanField(default=False)

    class Meta:
        unique_together = ['supplier_name', 'run_date','new_instock']

class stock_update_exceptions(models.Model):
    sku=models.AutoField(primary_key=True)
    comment=models.TextField(null=True)