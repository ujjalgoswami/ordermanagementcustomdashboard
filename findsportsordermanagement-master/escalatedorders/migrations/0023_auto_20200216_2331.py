# Generated by Django 2.2.4 on 2020-02-16 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalatedorders', '0022_auto_20200216_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_service_users',
            name='user_permission_level',
            field=models.IntegerField(default=0),
        ),
    ]