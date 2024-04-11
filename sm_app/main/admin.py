from django.contrib import admin
from main.models import Post, UserStats, LikedBy, Following
# Register your models here.


class ExtraShow(admin.ModelAdmin):
    readonly_fields =('id', 'created_at_formatted')

    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    created_at_formatted.short_description = 'Created At'

admin.site.register(Post, ExtraShow)
admin.site.register(UserStats, ExtraShow)
admin.site.register(LikedBy, ExtraShow)
admin.site.register(Following, ExtraShow)
