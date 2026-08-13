from django.contrib import admin
from .models import MQTTMessage


@admin.register(MQTTMessage)
class MQTTMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "message", "received_at")