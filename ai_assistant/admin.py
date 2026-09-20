from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "message_id",
        "patient",
        "message_type",
        "message",
        "created_at",
    )

    search_fields = (
        "message",
        "patient__name",
    )

    list_filter = (
        "message_type",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )