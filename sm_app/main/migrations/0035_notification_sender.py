# Generated by Django 5.0.6 on 2024-06-14 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_notification_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='sender',
            field=models.CharField(default='hello', max_length=300),
            preserve_default=False,
        ),
    ]
