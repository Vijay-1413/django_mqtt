import uuid

from django.db import models


class Log(models.Model):

    device_id = models.CharField(
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
        null=True,
        blank=True
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
        verbose_name = "Device Data"
        verbose_name_plural = "Device Data"

    def __str__(self):
        return self.device_id or "No Device ID"