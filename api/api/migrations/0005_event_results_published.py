# Generated by Django 5.0.3 on 2024-05-20 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_event_players_token_alter_player_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='results_published',
            field=models.BooleanField(default=False),
        ),
    ]
