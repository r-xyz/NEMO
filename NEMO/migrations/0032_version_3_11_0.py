from django.db import migrations, models

from NEMO.migrations_utils import create_news_for_version


class Migration(migrations.Migration):

    dependencies = [
        ('NEMO', '0031_version_3_10_0'),
    ]

    def new_version_news(apps, schema_editor):
        create_news_for_version(apps, "3.11.0")

    operations = [
        migrations.RunPython(new_version_news),
        migrations.CreateModel(
            name='ReservationQuestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of this ', max_length=100)),
                ('questions', models.TextField(help_text='Upon making a reservation, the user will be asked these questions. This field will only accept JSON format')),
                ('tool_reservations', models.BooleanField(default=True, help_text='Check this box to apply these questions to tool reservations')),
                ('area_reservations', models.BooleanField(default=False, help_text='Check this box to apply these questions to area reservations')),
                ('only_for_projects', models.ManyToManyField(blank=True, help_text='Select the projects these questions only apply to. Leave blank for all projects', to='NEMO.Project')),
            ],
            options={
                'verbose_name_plural': 'Reservation questions',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='reservation',
            name='question_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
