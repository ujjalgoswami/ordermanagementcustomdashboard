# Generated by Django 2.2.4 on 2020-01-05 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0015_suppliernew_reorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier_details',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]