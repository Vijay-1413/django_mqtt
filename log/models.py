from django.db import models


class Log(models.Model):
    device_id = models.CharField(
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
        verbose_name = "Device Data"
        verbose_name_plural = "Device Data"

    def __str__(self):
        return self.topic