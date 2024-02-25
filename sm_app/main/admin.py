from django.contrib import admin
from main.models import Post, UserStats, LikedBy, Following, User
# Register your models here.

class IdShow(admin.ModelAdmin):
    readonly_fields =('id',)

admin.site.register(Post, IdShow)
admin.site.register(UserStats, IdShow)
admin.site.register(LikedBy, IdShow)
admin.site.register(Following, IdShow)