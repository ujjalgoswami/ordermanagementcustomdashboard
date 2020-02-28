# Generated by Django 2.2.4 on 2020-02-16 20:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasklist', '0003_auto_20200216_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklist',
            name='paused',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='recurring_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('task_id', models.ForeignKey(db_column='task_id', on_delete=django.db.models.deletion.CASCADE, to='tasklist.tasklist')),
            ],
        ),
    ]