from django.contrib import admin
from main.models import Post, UserStats, LikedBy, Following, Comment, NestedComment, PostTag, Interest, ICF, PCF, InterestInteraction, PostInteraction, DateAndOrTimeSave, ArabaliConfigure, Notification, Category, Media
# Register your models here.


class ExtraShow(admin.ModelAdmin):
    readonly_fields =('id', 'date_created_formatted')

    def date_created_formatted(self, obj):
        return obj.date_created.strftime("%Y-%m-%d %H:%M:%S")

    date_created_formatted.short_description = 'Created At'

admin.site.register(Post, ExtraShow)
admin.site.register(UserStats, ExtraShow)
admin.site.register(LikedBy, ExtraShow)
admin.site.register(Following, ExtraShow)
admin.site.register(Comment, ExtraShow)
admin.site.register(NestedComment, ExtraShow)
admin.site.register(PostTag, ExtraShow)
admin.site.register(Interest, ExtraShow)
admin.site.register(ICF, ExtraShow)
admin.site.register(PCF, ExtraShow)
admin.site.register(InterestInteraction, ExtraShow)
admin.site.register(PostInteraction, ExtraShow)
admin.site.register(DateAndOrTimeSave, ExtraShow)
admin.site.register(ArabaliConfigure, ExtraShow)
admin.site.register(Notification, ExtraShow)
admin.site.register(Media, ExtraShow)
admin.site.register(Category, ExtraShow)