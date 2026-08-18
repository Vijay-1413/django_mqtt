from rest_framework import serializers


class CommandSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    message = serializers.CharField()
    message_type = serializers.CharField(default="cmd")
    timestamp = serializers.DateTimeField()