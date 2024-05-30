import signal
import json
import paho.mqtt.client as mqtt
import threading

MQTT_TOPIC = "/band/meds_dispenser"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

open = False


def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def func(open):
    if open:
        print("Pregrada je otvorena")
    else:
        print("Pregrada je zatvorena")


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    poruka = json.loads(msg.payload.decode())

    value = poruka["value"]

    if value == "open":
        func(True)
    elif value == "close":
        func(False)
    else:
        print("Unknown command received from the controller")

def fail(client, userdata, rc):
    print("CONNECTION FAILED")


def start_mqtt_subscriber():
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_connect_fail = fail
    client.on_disconnect = fail

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

if __name__ == "__main__":

    mqtt_client = start_mqtt_subscriber()
    signal.pause()