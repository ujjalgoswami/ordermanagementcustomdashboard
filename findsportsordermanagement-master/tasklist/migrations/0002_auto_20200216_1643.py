# Generated by Django 2.2.4 on 2020-02-16 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasklist', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasklist',
            old_name='end_date',
            new_name='completed_date',
        ),
        migrations.AddField(
            model_name='tasklist',
            name='estimated_end_date',
            field=models.DateField(null=True),
        ),
    ]
