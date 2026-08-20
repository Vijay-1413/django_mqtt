import json
import uuid

import paho.mqtt.client as mqtt
from django.utils import timezone

from .models import MQTTMessage
from devicedetails.models import Device
from devicedata.models import Log


BROKER = "mqtt.febinoo.com"
PORT = 1883

PUBLISH_1 = "alms/cmd"
PUBLISH_2 = "alms/serverresp"
PUBLISH_USERCMD = "alms/usercmd"
PUBLISH_USERRESP = "alms/userresp"

SUBSCRIBE_1 = "alms/beat/#"
SUBSCRIBE_2 = "alms/deviceresp/#"
SUBSCRIBE_3 = "alms/usercmd/#"

client_global = None


def get_device(device_id):
    return Device.objects.filter(
        device_id=device_id
    ).first()


def parse_timestamp(timestamp):
    if not timestamp:
        return None

    return timezone.datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    )


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

    command_data = {
        "device_id": device_id,
        "message": message_text,
        "message_type": message_type,
        "message_id": str(message_id),
        "timestamp": timestamp.isoformat()
    }

    message = json.dumps(command_data)

    topic = f"{PUBLISH_1}/{device_id}"

    if client_global is None:
        raise Exception("MQTT client is not connected")

    result = client_global.publish(
        topic,
        message,
        qos=1
    )

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

    if device is not None:
        save_log(
            device_id,
            topic,
            message_type,
            message_id,
            message,
            "send",
            timestamp
        )

    print("Command sent:", topic)


def publish_user_command(
    client,
    device,
    device_id,
    message_text
):
    message_id = uuid.uuid4()
    timestamp = timezone.now()

    command_data = {
        "device_id": device_id,
        "message": message_text,
        "message_type": "usercmd",
        "message_id": str(message_id),
        "timestamp": timestamp.isoformat()
    }

    command_message = json.dumps(command_data)

    topic = f"{PUBLISH_1}/{device_id}"

    print("USER COMMAND TOPIC:", topic)
    print("USER COMMAND MESSAGE:", command_message)

    result = client.publish(
        topic,
        command_message,
        qos=0
    )

    print("PUBLISH RESULT:", result.rc)

    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            "USER COMMAND PUBLISH FAILED:",
            device_id
        )
        return

    save_message(
        device,
        device_id,
        topic,
        "usercmd",
        message_id,
        command_message,
        "send",
        timestamp
    )

    save_log(
        device_id,
        topic,
        "usercmd",
        message_id,
        command_message,
        "send",
        timestamp
    )

    print("USER COMMAND SENT:", topic)


def publish_user_response(
    client,
    device,
    device_id,
    message_text
):
    topic = f"{PUBLISH_USERRESP}/{device_id}"

    result = client.publish(
        topic,
        message_text,
        qos=1
    )

    print(
        "USER RESPONSE PUBLISH RESULT:",
        result.rc
    )

    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            "USER RESPONSE PUBLISH FAILED:",
            device_id
        )
        return

    print(
        "USER RESPONSE SENT:",
        topic
    )


def publish_heartbeat_response(
    client,
    device_id,
    data
):
    response = {
        "device_id": device_id,
        "timestamp": data.get("timestamp"),
        "message_type": data.get("message_type"),
        "message": data.get("message"),
        "message_id": str(data.get("message_id"))
    }

    response_message = json.dumps(response)

    response_topic = f"{PUBLISH_2}/{device_id}"

    result = client.publish(
        response_topic,
        response_message,
        qos=1
    )

    print(
        "HEARTBEAT RESPONSE PUBLISH RESULT:",
        result.rc
    )

    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            "HEARTBEAT RESPONSE FAILED:",
            device_id
        )
        return

    print(
        "HEARTBEAT RESPONSE SENT:",
        response_topic
    )


def publish_device_response(
    client,
    device,
    device_id,
    message_id,
    timestamp
):
    response_timestamp = timezone.now()

    response = {
        "device_id": device_id,
        "status": "OK",
        "message": "SOK",
        "message_type": "serverresp",
        "message_id": str(message_id),
        "timestamp": timestamp
    }

    response_message = json.dumps(response)

    response_topic = f"{PUBLISH_2}/{device_id}"

    print(
        "SERVER RESPONSE TOPIC:",
        response_topic
    )

    print(
        "SERVER RESPONSE MESSAGE:",
        response_message
    )

    result = client.publish(
        response_topic,
        response_message,
        qos=1
    )

    print(
        "SERVER RESPONSE PUBLISH RESULT:",
        result.rc
    )

    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(
            "SERVER RESPONSE FAILED:",
            device_id
        )
        return

    save_message(
        device,
        device_id,
        response_topic,
        "serverresp",
        message_id,
        response_message,
        "send",
        response_timestamp
    )

    save_log(
        device_id,
        response_topic,
        "serverresp",
        message_id,
        response_message,
        "send",
        response_timestamp
    )

    print(
        "SERVER RESPONSE SAVED TO MQTTMESSAGE"
    )

    print(
        "SERVER RESPONSE SAVED TO LOG"
    )


def handle_usercmd(
    client,
    topic,
    payload
):
    parts = topic.split("/")

    if len(parts) != 3:
        print(
            "INVALID USERCMD TOPIC:",
            topic
        )
        return

    device_id = parts[2]

    message_text = payload.decode(
        "utf-8"
    )

    device = get_device(device_id)

    if device is None:
        message_id = uuid.uuid4()
        timestamp = timezone.now()

        save_message(
            None,
            device_id,
            topic,
            "usercmd",
            message_id,
            message_text,
            "receive",
            timestamp
        )

        print(
            "DEVICE NOT FOUND"
        )

        print(
            "USERCMD SAVED TO MQTTMESSAGE:",
            device_id
        )

        return

    print(
        "DEVICE EXISTS:",
        device_id
    )

    publish_user_command(
        client,
        device,
        device_id,
        message_text
    )


def handle_heartbeat(
    client,
    topic,
    payload
):
    parts = topic.split("/")

    if len(parts) != 3:
        print(
            "INVALID HEARTBEAT TOPIC:",
            topic
        )
        return

    device_id = parts[2]

    data = json.loads(
        payload.decode("utf-8")
    )

    timestamp = data.get(
        "timestamp"
    )

    if not timestamp:
        print(
            "HEARTBEAT TIMESTAMP MISSING:",
            device_id
        )
        return

    device = get_device(
        device_id
    )

    if device is None:
        print(
            "DEVICE NOT FOUND:",
            device_id
        )
        return

    device_timestamp = parse_timestamp(
        timestamp
    )

    device.last_beat = device_timestamp

    device.save(
        update_fields=[
            "last_beat"
        ]
    )

    print(
        "LAST_BEAT UPDATED:",
        device_id,
        device_timestamp
    )

    message_id = data.get(
        "message_id"
    )

    if not message_id:
        print(
            "HEARTBEAT MESSAGE ID MISSING:",
            device_id
        )
        return

    try:
        uuid.UUID(
            str(message_id)
        )
    except ValueError:
        print(
            "INVALID HEARTBEAT UUID:",
            message_id
        )
        return

    publish_heartbeat_response(
        client,
        device_id,
        data
    )


def handle_deviceresp(
    client,
    topic,
    payload
):
    parts = topic.split("/")

    if len(parts) != 3:
        print(
            "INVALID DEVICERESP TOPIC:",
            topic
        )
        return

    device_id = parts[2]

    data = json.loads(
        payload.decode("utf-8")
    )

    message_id = data.get(
        "message_id"
    )

    if not message_id:
        message_id = str(
            uuid.uuid4()
        )

    message_type = data.get(
        "message_type",
        "deviceresp"
    )

    timestamp = data.get(
        "timestamp"
    )

    device_timestamp = parse_timestamp(
        timestamp
    )

    message = json.dumps(
        data
    )

    device = get_device(
        device_id
    )

    save_message(
        device,
        device_id,
        topic,
        message_type,
        message_id,
        message,
        "receive",
        device_timestamp
    )

    print(
        "DEVICERESP SAVED TO MQTTMESSAGE:",
        device_id
    )

    if device is None:
        print(
            "DEVICE NOT FOUND - LOG NOT SAVED:",
            device_id
        )
        return

    save_log(
        device_id,
        topic,
        message_type,
        message_id,
        message,
        "receive",
        device_timestamp
    )

    print(
        "DEVICERESP SAVED TO LOG:",
        device_id
    )

    publish_device_response(
        client,
        device,
        device_id,
        message_id,
        timestamp
    )

    message_text = data.get(
        "message"
    )

    if message_text is not None:
        publish_user_response(
            client,
            device,
            device_id,
            str(message_text)
        )


def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print(
        "MQTT Connected:",
        reason_code
    )

    client.subscribe(
        SUBSCRIBE_1,
        qos=1
    )

    client.subscribe(
        SUBSCRIBE_2,
        qos=1
    )

    client.subscribe(
        SUBSCRIBE_3,
        qos=1
    )

    print(
        "Subscribed:",
        SUBSCRIBE_1
    )

    print(
        "Subscribed:",
        SUBSCRIBE_2
    )

    print(
        "Subscribed:",
        SUBSCRIBE_3
    )


def on_message(
    client,
    userdata,
    msg
):
    try:
        topic = msg.topic
        payload = msg.payload

        print()
        print(
            "======================================"
        )
        print(
            "MESSAGE RECEIVED"
        )
        print(
            "TOPIC:",
            topic
        )
        print(
            "PAYLOAD:",
            payload
        )
        print(
            "======================================"
        )

        if topic.startswith(
            f"{PUBLISH_USERCMD}/"
        ):
            handle_usercmd(
                client,
                topic,
                payload
            )
            return

        if topic.startswith(
            "alms/beat/"
        ):
            handle_heartbeat(
                client,
                topic,
                payload
            )
            return

        if topic.startswith(
            "alms/deviceresp/"
        ):
            handle_deviceresp(
                client,
                topic,
                payload
            )
            return

        print(
            "UNKNOWN TOPIC:",
            topic
        )

    except json.JSONDecodeError as error:
        print(
            "INVALID JSON:",
            repr(error)
        )

    except (
        ValueError,
        TypeError
    ) as error:
        print(
            "INVALID TIMESTAMP OR DATA:",
            repr(error)
        )

    except Exception as error:
        print(
            "MQTT ERROR:",
            repr(error)
        )


def start_mqtt():
    global client_global

    client_global = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client_global.on_connect = on_connect
    client_global.on_message = on_message

    print(
        "Connecting to MQTT broker..."
    )

    client_global.connect(
        BROKER,
        PORT,
        60
    )

    print(
        "Starting MQTT loop..."
    )

    client_global.loop_forever()