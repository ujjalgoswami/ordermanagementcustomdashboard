# Generated by Django 2.2.4 on 2020-02-12 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0020_auto_20200206_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier_details',
            name='stock_update_buy_plan_id',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='supplier_details',
            name='stock_update_url',
            field=models.TextField(null=True),
        ),
    ]
