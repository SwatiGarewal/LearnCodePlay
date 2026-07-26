from django.contrib import admin
from .models import *


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ('game_id', 'user', 'comment_text', 'created_at')
    list_filter = ('game_id', 'created_at')
    search_fields = ('comment_text', 'game_id')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'image',
        'user',
        'get_email',
        'mobile',
        'gender',
        'dob',
        'profession',
        
    )
    search_fields = ('user__username', 'user__email', 'mobile')
    list_filter = ('gender', 'profession')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'