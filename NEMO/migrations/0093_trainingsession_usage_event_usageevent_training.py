# Generated by Django 4.2.16 on 2024-11-01 22:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("NEMO", "0092_alter_accounttype_name_alter_alert_category_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainingsession",
            name="usage_event",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="NEMO.usageevent"
            ),
        ),
        migrations.AddField(
            model_name="usageevent",
            name="training",
            field=models.BooleanField(default=False),
        ),
    ]