from django.contrib import admin
from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "topic",
        "message",
        "timestamp",
        "device_timestamp",
    )