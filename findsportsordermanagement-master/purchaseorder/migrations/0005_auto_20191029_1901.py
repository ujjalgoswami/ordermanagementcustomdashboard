# Generated by Django 2.2.4 on 2019-10-29 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0004_auto_20191029_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='instock',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='qty',
            field=models.IntegerField(),
        ),
    ]
