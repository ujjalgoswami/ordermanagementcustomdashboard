# Generated by Django 2.2.4 on 2020-01-09 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalatedorders', '0009_auto_20200109_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_service_users',
            name='c_id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]