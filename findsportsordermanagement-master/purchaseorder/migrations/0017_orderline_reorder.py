# Generated by Django 2.2.4 on 2019-11-29 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0016_purchaseorder_received_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderline',
            name='reorder',
            field=models.BooleanField(default=False),
        ),
    ]
