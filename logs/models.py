import uuid

from django.db import models
from devicedetails.models import Device


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

    topic = models.CharField(
        max_length=255
    )

    message_type = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    message_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    message = models.TextField()

    send_receive = models.CharField(
        max_length=10,
        choices=[
            ("send", "Send"),
            ("receive", "Receive"),
        ],
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    device_timestamp = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "logs"
        verbose_name_plural = "logs"

    def __str__(self):
        return self.received_device_id or "No Device ID"