# Generated by Django 2.2.4 on 2019-12-29 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timebomb', '0006_timebomb'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timebomb',
            name='id',
        ),
        migrations.AlterField(
            model_name='timebomb',
            name='sku',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
