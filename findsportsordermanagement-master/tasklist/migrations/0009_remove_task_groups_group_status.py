# Generated by Django 2.2.4 on 2020-02-17 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasklist', '0008_auto_20200217_1310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task_groups',
            name='group_status',
        ),
    ]