from django.contrib import admin
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice, MessageNotificationSetting
# Register your models here.
class ExtraShow(admin.ModelAdmin):
    readonly_fields =('id', 'created_at_formatted')

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    created_at_formatted.short_description = 'Created At'

admin.site.register(ChatRoom, ExtraShow)
admin.site.register(Message, ExtraShow)
admin.site.register(MessageNotificationSetting, ExtraShow)
admin.site.register(PollMessage, ExtraShow)
admin.site.register(PollOption, ExtraShow)
admin.site.register(PollingChoice, ExtraShow)