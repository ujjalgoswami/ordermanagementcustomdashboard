# Generated by Django 2.2.4 on 2020-01-29 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_email_history_handler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email_history',
            name='order_id',
            field=models.TextField(),
        ),
    ]
