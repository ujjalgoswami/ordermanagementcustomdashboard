# Generated by Django 2.2.4 on 2020-02-12 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0021_auto_20200212_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier_details',
            name='stock_update_brand_name',
            field=models.TextField(null=True),
        ),
    ]
