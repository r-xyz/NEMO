# Generated by Django 4.2.16 on 2024-11-09 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sensors", "0002_alter_sensor_data_label_alter_sensor_data_prefix_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sensordata",
            name="created_date",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]