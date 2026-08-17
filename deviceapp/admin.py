from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        'device_id',
        'device_name',
        'device_type',
        'hardware_version',
        'software_version',
        'last_beat'
    )