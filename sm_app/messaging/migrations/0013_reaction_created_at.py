# Generated by Django 5.0.6 on 2024-08-25 22:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("messaging", "0012_alter_reaction_message_alter_reaction_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="reaction",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]