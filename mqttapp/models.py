from django.db import models


class MQTTMessage(models.Model):
    topic = models.CharField(max_length=255)
    message = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message