# Generated by Django 2.2.4 on 2020-01-09 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escalatedorders', '0005_auto_20200105_0944'),
    ]

    operations = [
        migrations.CreateModel(
            name='customer_service_users',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
    ]
