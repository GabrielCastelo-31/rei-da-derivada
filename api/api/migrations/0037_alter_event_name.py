# Generated by Django 5.0.3 on 2024-10-03 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_alter_sumulaclassificatoria_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(default='', max_length=64, null=True),
        ),
    ]
