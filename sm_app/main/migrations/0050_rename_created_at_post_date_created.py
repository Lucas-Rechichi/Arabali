# Generated by Django 5.0.6 on 2025-01-09 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0049_rename_catergory_category"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="created_at",
            new_name="date_created",
        ),
    ]