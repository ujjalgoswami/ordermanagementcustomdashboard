# Generated by Django 2.2.4 on 2020-02-06 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0020_auto_20200206_1033'),
        ('stockupdate', '0008_auto_20200204_1050'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stockupdate',
            unique_together={('supplier_name', 'run_date', 'new_instock')},
        ),
    ]