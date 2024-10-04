# Generated by Django 4.2.11 on 2024-08-27 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("NEMO", "0088_alter_configurationoption_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="door",
            name="farewell_message",
            field=models.TextField(
                blank=True,
                help_text="The farewell message will be displayed on the tablet logout page. You can use HTML and JavaScript.",
                null=True,
            ),
        ),
    ]