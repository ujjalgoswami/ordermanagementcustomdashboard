# Generated by Django 2.2.4 on 2020-01-19 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockupdate', '0004_auto_20200118_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockupdate',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]
