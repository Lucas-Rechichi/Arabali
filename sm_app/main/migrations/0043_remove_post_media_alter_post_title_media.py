# Generated by Django 5.0.6 on 2024-11-24 03:08

import django.db.models.deletion
import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0042_rename_subscribers_following_name_alter_comment_post"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="media",
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name="Media",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "media_obj",
                    models.FileField(
                        null=True, upload_to=main.models.get_media_upload_path_posts
                    ),
                ),
                ("caption", models.CharField(max_length=50)),
                (
                    "post",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="post",
                        to="main.post",
                    ),
                ),
            ],
        ),
    ]