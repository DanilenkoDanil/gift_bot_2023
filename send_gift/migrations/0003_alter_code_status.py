# Generated by Django 4.0.4 on 2023-09-10 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('send_gift', '0002_game_game_link_game_game_sub_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code',
            name='status',
            field=models.CharField(max_length=200),
        ),
    ]
