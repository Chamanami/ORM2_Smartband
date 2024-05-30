import pygame
import time
import paho.mqtt.client as mqtt
import signal
import json

MQTT_TOPIC = "/band/sound"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def func():
    time_to_play = 5
    pauza = 0.75

    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load('pomoc.mp3')

    end_time = time.time() + time_to_play

    # Pustite zvuk i dodajte pauzu između repeticija
    while time.time() < end_time:
        
        pygame.mixer.music.play()
        time.sleep(pauza)

    pygame.mixer.music.stop()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    poruka = json.loads(msg.payload.decode())

    value = poruka["value"]

    if value == "pomoc":
        func()
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