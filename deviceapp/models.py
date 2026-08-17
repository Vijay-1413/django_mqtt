from django.db import models


class Device(models.Model):
    device_id = models.CharField(
        max_length=100,
        unique=True,
        primary_key=True
    )
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100)
    hardware_version = models.CharField(max_length=50)
    software_version = models.CharField(max_length=50)
    last_beat=models.DateTimeField(null=True,
        blank=True)
    
    class Meta:
        verbose_name = "Device Details"
        verbose_name_plural = "Device Details"

    def __str__(self):
        return self.device_id