# Generated by Django 2.2.4 on 2019-12-29 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timebomb', '0002_auto_20191229_0507'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timebomb',
            name='active',
        ),
    ]
