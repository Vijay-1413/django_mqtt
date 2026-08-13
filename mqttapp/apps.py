from django.apps import AppConfig
import threading


class MqttappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mqttapp"

    def ready(self):
        from .mqtt_service import start_mqtt

        if not any(
            thread.name == "mqtt_thread"
            for thread in threading.enumerate()
        ):
            threading.Thread(
                target=start_mqtt,
                name="mqtt_thread",
                daemon=True
            ).start()