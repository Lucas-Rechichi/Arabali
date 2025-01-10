from django.contrib import admin
from messaging.models import ChatRoom, Message, PollMessage, PollOption, PollingChoice, MessageNotificationSetting, Reaction
# Register your models here.
class ExtraShow(admin.ModelAdmin):
    readonly_fields =('id', 'date_created_formatted')

    def date_created_formatted(self, obj):
        return obj.date_created.strftime("%Y-%m-%d %H:%M:%S")

    date_created_formatted.short_description = 'Created At'

admin.site.register(ChatRoom, ExtraShow)
admin.site.register(Message, ExtraShow)
admin.site.register(MessageNotificationSetting, ExtraShow)
admin.site.register(PollMessage, ExtraShow)
admin.site.register(PollOption, ExtraShow)
admin.site.register(PollingChoice, ExtraShow)
admin.site.register(Reaction, ExtraShow)