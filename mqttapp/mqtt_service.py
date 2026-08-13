import paho.mqtt.client as mqtt
from .models import MQTTMessage

BROKER = "mqtt.febinoo.com"
PORT = 1883
TOPIC = "Test"


def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT Connected")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    message = msg.payload.decode()

    MQTTMessage.objects.create(
        topic=msg.topic,
        message=message
    )

    print("Message stored:", message)


def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)

    client.loop_forever()