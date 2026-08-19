import json
import uuid

import paho.mqtt.client as mqtt
from django.utils import timezone

from .models import MQTTMessage
from deviceapp.models import Device
from log.models import Log


BROKER = "mqtt.febinoo.com"
PORT = 1883

PUBLISH_1 = "alms/cmd"
PUBLISH_2 = "alms/serverresp"

SUBSCRIBE_1 = "alms/beat/#"
SUBSCRIBE_2 = "alms/deviceresp/#"


def get_device(device_id):
    return Device.objects.filter(
        device_id=device_id
    ).first()


def save_message(
    device,
    device_id,
    topic,
    message_type,
    message_id,
    message,
    send_receive,
    device_timestamp
):
    MQTTMessage.objects.create(
        device=device,
        received_device_id=device_id,
        topic=topic,
        message_type=message_type,
        message_id=message_id,
        message=message,
        send_receive=send_receive,
        device_timestamp=device_timestamp
    )


def save_log(
    device_id,
    topic,
    message_type,
    message_id,
    message,
    send_receive,
    device_timestamp
):
    Log.objects.create(
        device_id=device_id,
        topic=topic,
        message_type=message_type,
        message_id=message_id,
        message=message,
        send_receive=send_receive,
        device_timestamp=device_timestamp
    )


def publish_command(data):
    device_id = data["device_id"]
    message_text = data["message"]
    message_type = data["message_type"]

    device = get_device(device_id)

    message_id = uuid.uuid4()
    timestamp = timezone.now()

    data = {
        "device_id": device_id,
        "message": message_text,
        "message_type": message_type,
        "message_id": str(message_id),
        "timestamp": timestamp.isoformat()
    }

    message = json.dumps(data)

    topic = f"{PUBLISH_1}/{device_id}"

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        result = client.publish(topic, message, qos=1)
        result.wait_for_publish()

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise Exception("MQTT publish failed")

        save_message(
            device,
            device_id,
            topic,
            message_type,
            message_id,
            message,
            "send",
            timestamp
        )

        if device:
            save_log(
                device_id,
                topic,
                message_type,
                message_id,
                message,
                "send",
                timestamp
            )

    finally:
        client.loop_stop()
        client.disconnect()


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    print("MQTT Connected:", reason_code)

    client.subscribe(
        SUBSCRIBE_1,
        qos=1
    )

    client.subscribe(
        SUBSCRIBE_2,
        qos=1
    )

    print("Subscribed:", SUBSCRIBE_1)
    print("Subscribed:", SUBSCRIBE_2)


def on_message(client, userdata, msg):

    try:
        data = json.loads(
            msg.payload.decode("utf-8")
        )

        device_id = data.get("device_id")

        if not device_id:
            return

        device = get_device(device_id)

        message_type = data.get(
            "message_type"
        )

        message_id = uuid.uuid4()

        timestamp = data.get(
            "timestamp"
        )

        device_timestamp = None

        if timestamp:
            device_timestamp = timezone.datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

        message = json.dumps(data)

        save_message(
            device,
            device_id,
            msg.topic,
            message_type,
            message_id,
            message,
            "receive",
            device_timestamp
        )

        if not device:
            print(
                "Device not found:",
                device_id
            )
            return

        save_log(
            device_id,
            msg.topic,
            message_type,
            message_id,
            message,
            "receive",
            device_timestamp
        )

        if msg.topic.startswith("alms/beat/"):

            if device_timestamp:
                device.last_beat = device_timestamp

                device.save(
                    update_fields=["last_beat"]
                )

            print(
                "Beat received:",
                device_id
            )

        elif msg.topic.startswith("alms/deviceresp/"):

            response_id = uuid.uuid4()
            response_timestamp = timezone.now()

            response = {
                "device_id": device_id,
                "status": "OK",
                "message": "SOK",
                "message_type": "serverresp",
                "message_id": str(response_id),
                "timestamp": timestamp
            }

            response_message = json.dumps(
                response
            )

            response_topic = (
                f"{PUBLISH_2}/{device_id}"
            )

            result = client.publish(
                response_topic,
                response_message,
                qos=1
            )

            result.wait_for_publish()

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print("Response failed")
                return

            save_message(
                device,
                device_id,
                response_topic,
                "serverresp",
                response_id,
                response_message,
                "send",
                response_timestamp
            )

            save_log(
                device_id,
                response_topic,
                "serverresp",
                response_id,
                response_message,
                "send",
                response_timestamp
            )

            print(
                "SOK sent:",
                response_topic
            )


    except json.JSONDecodeError:
        print("Invalid JSON")

    except (ValueError, TypeError):
        print("Invalid timestamp")

    except Exception as error:
        print("MQTT Error:", error)


def start_mqtt():

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to MQTT broker...")

    client.connect(
        BROKER,
        PORT,
        60
    )

    print("Starting MQTT loop...")

    client.loop_forever()