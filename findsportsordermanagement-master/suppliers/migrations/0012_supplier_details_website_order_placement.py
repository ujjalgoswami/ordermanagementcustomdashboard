# Generated by Django 2.2.4 on 2019-10-26 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0011_delete_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier_details',
            name='website_order_placement',
            field=models.BooleanField(default=False),
        ),
    ]
