# Generated by Django 5.0.6 on 2024-06-12 20:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_notification_notificationsettingobject'),
        ('messaging', '0003_alter_chatroom_icon_alter_chatroom_room_bg_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageNotificationSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('messages', models.BooleanField()),
                ('replies', models.BooleanField()),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messaging.chatroom')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userstats')),
            ],
        ),
        migrations.DeleteModel(
            name='NotificationSettingObject',
        ),
    ]
