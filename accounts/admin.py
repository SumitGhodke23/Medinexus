from django.contrib import admin
from .models import Notification, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "role")
	list_filter = ("role",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "kind", "title", "read_at", "created_at")
	list_filter = ("kind", "read_at")
	search_fields = ("user__username", "title", "message")
