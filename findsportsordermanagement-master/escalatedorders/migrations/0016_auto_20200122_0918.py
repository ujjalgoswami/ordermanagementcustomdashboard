# Generated by Django 2.2.4 on 2020-01-22 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalatedorders', '0015_independentescalatedtickets_created_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_service_users',
            name='average_time',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer_service_users',
            name='score',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='escalatedorders',
            name='created_date',
            field=models.DateField(null=True),
        ),
    ]
