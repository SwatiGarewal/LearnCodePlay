from django.contrib import admin
from .models import GameComment


@admin.register(GameComment)
class GameCommentAdmin(admin.ModelAdmin):
    list_display = ('game_id', 'user', 'comment_text', 'created_at')
    list_filter = ('game_id', 'created_at')
    search_fields = ('comment_text', 'game_id')
