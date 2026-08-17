import json
from datetime import datetime

import paho.mqtt.client as mqtt

from .models import MQTTMessage
from deviceapp.models import Device
from log.models import Log


BROKER = "mqtt.febinoo.com"
PORT = 1883

TOPIC = "request"
REQUEST_TOPIC = "response"


def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT Connected")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        device_id = data.get("device_id")
        timestamp = data.get("timestamp")

        if timestamp:
            timestamp = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

        message = json.dumps(data, indent=4)

        try:
            device = Device.objects.get(
                device_id=device_id
            )
        except Device.DoesNotExist:
            device = None
        
        if device and data.get("type") == "beat":
            device.last_beat = timestamp
            device.save(update_fields=["last_beat"])
        
            request_message = {
                "device_id": device_id,
                "status": "OK",
                "type": "beat",
                "timestamp": data.get("timestamp")
            }

            client.publish(
                REQUEST_TOPIC,
                json.dumps(request_message)
            )

        MQTTMessage.objects.create(
            device=device,
            received_device_id=device_id,
            topic=msg.topic,
            message=message,
            device_timestamp=timestamp
        )

        if device:
            Log.objects.create(
                device_id=device_id,
                topic=msg.topic,
                message=message,
                device_timestamp=timestamp
            )

            request_message = {
                "device_id": device_id,
                "status": "OK",
                "type":"data",
                "timestamp": data.get("timestamp")
            }

            client.publish(
                REQUEST_TOPIC,
                json.dumps(request_message)
            )

            print("Request sent:", request_message)

    except json.JSONDecodeError:
        print("Invalid JSON")

    except ValueError:
        print("Invalid timestamp")

    except Exception as error:
        print("Error:", error)


def start_mqtt():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    client.loop_forever()