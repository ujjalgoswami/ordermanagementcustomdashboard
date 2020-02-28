from django.db import models

# Create your models here.

class SupplierNew(models.Model):
    order_line_id = models.CharField(max_length=100, primary_key=True)
    order_id=models.CharField(max_length=100,null=True)
    sku = models.TextField()
    primarysupplier = models.TextField()
    purchase_order_generated=models.BooleanField(default=False)
    reorder = models.BooleanField(default=False)



class Supplier_Details(models.Model):

    supplier_name=models.CharField(max_length=200,primary_key=True)
    supplier_email = models.CharField(max_length=300,default="NA")
    minimum_order = models.CharField(max_length=100,null=True)
    website_name=models.CharField(max_length=100,null=True)
    website_link = models.TextField(null=True)
    username=models.CharField(max_length=200,null=True)
    password=models.CharField(max_length=200,null=True)
    short_code=models.CharField(max_length=100,null=True)
    website_order_placement = models.BooleanField(default=False)
    onhold=models.BooleanField(default=False)
    onhold_date = models.DateField(null=True)
    contact_name=models.TextField(null=True)
    contact_email = models.TextField(null=True)
    contact_number = models.TextField(null=True)
    contact_position = models.TextField(null=True)
    disabled = models.BooleanField(default=False)
    last_stock_update=models.DateField(null=True)
    last_stock_update_filename = models.TextField(null=True)
    stock_take_possible = models.BooleanField(default=False)
    stock_update_buy_plan_id = models.TextField(null=True)
    stock_update_url = models.TextField(null=True)
    stock_update_brand_name = models.TextField(null=True)


    def __str__(self):
        readonly_fields = ["supplier_name"]
        template = '{0.supplier_name}'
        return template.format(self)

