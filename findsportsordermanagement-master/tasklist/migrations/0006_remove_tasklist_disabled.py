# Generated by Django 2.2.4 on 2020-02-16 22:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasklist', '0005_recurring_task_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasklist',
            name='disabled',
        ),
    ]
