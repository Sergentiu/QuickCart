from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'message_preview', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    list_per_page = 50
    readonly_fields = ('timestamp',)

    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message Preview'
