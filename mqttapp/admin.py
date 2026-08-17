from django.contrib import admin
from .models import MQTTMessage


@admin.register(MQTTMessage)
class MQTTMessageAdmin(admin.ModelAdmin):
    list_display = (
        "received_device_id",
        "topic",
        "message",
        "timestamp",
    )