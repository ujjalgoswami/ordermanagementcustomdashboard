# Generated by Django 2.2.4 on 2020-02-18 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasklist', '0010_tasklist_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklist',
            name='extension_taken',
            field=models.BooleanField(default=False),
        ),
    ]