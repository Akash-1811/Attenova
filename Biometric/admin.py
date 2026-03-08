from django.contrib import admin

from Biometric.models import BiometricDevice


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "name", "office", "is_active", "created_at")
    list_filter = ("is_active", "office")
    search_fields = ("device_id", "name", "office__name")
