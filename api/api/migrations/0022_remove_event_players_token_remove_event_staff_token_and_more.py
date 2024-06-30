# Generated by Django 5.0.3 on 2024-06-29 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_playerscore_event_alter_playerscore_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='players_token',
        ),
        migrations.RemoveField(
            model_name='event',
            name='staff_token',
        ),
        migrations.AddField(
            model_name='event',
            name='join_token',
            field=models.CharField(blank=True, default='', max_length=9),
        ),
    ]
