from django.contrib import admin

from Notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "created_by", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "recipient__email", "created_by__email")
    readonly_fields = ("created_at",)
