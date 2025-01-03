# Generated by Django 5.0.6 on 2024-11-20 23:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0041_alter_comment_liked_by_alter_nestedcomment_liked_by_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="following",
            old_name="subscribers",
            new_name="name",
        ),
        migrations.AlterField(
            model_name="comment",
            name="post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="main.post",
            ),
        ),
    ]
