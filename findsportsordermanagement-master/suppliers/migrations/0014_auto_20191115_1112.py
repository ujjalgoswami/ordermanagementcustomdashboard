# Generated by Django 2.2.4 on 2019-11-15 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0013_auto_20191029_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier_details',
            name='contact_email',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='supplier_details',
            name='contact_name',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='supplier_details',
            name='contact_number',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='supplier_details',
            name='contact_position',
            field=models.TextField(null=True),
        ),
    ]
