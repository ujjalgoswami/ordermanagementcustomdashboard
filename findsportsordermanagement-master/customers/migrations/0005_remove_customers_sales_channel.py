# Generated by Django 2.2.4 on 2019-10-06 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_auto_20191006_0619'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customers',
            name='sales_channel',
        ),
    ]
