import json
from datetime import datetime
import paho.mqtt.client as mqtt

from mqttapp.models import MQTTMessage


BROKER = "mqtt.febinoo.com"
PORT = 1883
TOPIC = "cmd"


def publish_command(data):

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    try:
        client.connect(BROKER, PORT, 60)

        data["timestamp"] = datetime.now().isoformat()

        message = json.dumps(data)

        result = client.publish(
            TOPIC,
            message
        )

        result.wait_for_publish()

        if result.rc == mqtt.MQTT_ERR_SUCCESS:

            MQTTMessage.objects.create(
                received_device_id=data.get("device_id"),
                topic=TOPIC,
                message=message,
                send_receive="send"
            )

            print("Message sent:", data)

        else:
            print("Message was not sent")
            print("MQTT error:", result.rc)

    finally:
        client.disconnect()