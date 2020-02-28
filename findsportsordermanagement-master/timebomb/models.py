from django.db import models

# Create your models here.
class timebomb(models.Model):
    sku = models.CharField(max_length=100,primary_key=True)
    day=models.CharField(max_length=15)
    promotion_expiry=models.CharField(max_length=50)
    active=models.BooleanField(default=False)

    class Meta:
        unique_together = ['sku', 'day']