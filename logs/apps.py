import os
import threading

from django.apps import AppConfig


class LogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logs"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .mqtt_service import start_mqtt

        thread = threading.Thread(
            target=start_mqtt,
            daemon=True,
            name="mqtt_thread"
        )

        thread.start()