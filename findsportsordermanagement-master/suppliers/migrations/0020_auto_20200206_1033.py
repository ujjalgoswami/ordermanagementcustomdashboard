# Generated by Django 2.2.4 on 2020-02-06 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0019_supplier_details_stock_take_automated'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplier_details',
            old_name='stock_take_automated',
            new_name='stock_take_possible',
        ),
    ]
