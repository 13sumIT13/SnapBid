# Generated by Django 5.1.5 on 2025-05-04 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_productimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='auction_winner_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auction',
            name='five_min_warning_sent',
            field=models.BooleanField(default=False),
        ),
    ]
