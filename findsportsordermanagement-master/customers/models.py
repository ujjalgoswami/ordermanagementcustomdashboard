from django.db import models

# Create your models here.
class Customers(models.Model):
    order_id=models.CharField(max_length=100,primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=200,null=True)