from django.db import models

# Create your models here.

class newsletter(models.Model):
    product_sku=models.CharField(max_length=100,null=True)
    product_description=models.TextField(null=True)
    product_link=models.TextField(null=True)
    product_image_link=models.TextField(null=True)
    product_width = models.CharField(max_length=5)
    product_height = models.CharField(max_length=5)
    product_alias = models.CharField(max_length=100)
    product_price_starting_from = models.CharField(max_length=100,null=True)
    product_type=models.CharField(max_length=100,default="product",null=True)
    product_row=models.IntegerField(null=True)



