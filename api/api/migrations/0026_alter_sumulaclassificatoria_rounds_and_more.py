# Generated by Django 5.0.3 on 2024-07-31 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_playerscore_rounds_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sumulaclassificatoria',
            name='rounds',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='sumulaimortal',
            name='rounds',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
