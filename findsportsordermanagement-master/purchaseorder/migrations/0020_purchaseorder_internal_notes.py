# Generated by Django 2.2.4 on 2019-12-10 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0019_remove_purchaseorder_internal_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='internal_notes',
            field=models.TextField(default=''),
        ),
    ]
