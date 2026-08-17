from django.db import models
from deviceapp.models import Device


class MQTTMessage(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    received_device_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    topic = models.CharField(max_length=200)
    message = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    device_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Logs"
        verbose_name_plural = "Logs"

    def __str__(self):
        return self.received_device_id or "No Device ID"