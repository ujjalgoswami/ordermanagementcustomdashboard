# Generated by Django 2.2.4 on 2019-11-14 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0013_purchaseorder_received_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='received_date',
            field=models.BooleanField(default=False),
        ),
    ]