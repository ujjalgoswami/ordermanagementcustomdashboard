# Generated by Django 2.2.4 on 2019-10-06 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netoapihook', '0011_remove_orderhistory_test_col'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderhistory',
            name='sales_channel',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
