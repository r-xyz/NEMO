# Generated by Django 3.2.18 on 2023-03-08 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0046_auto_20230307_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='safetyissue',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
