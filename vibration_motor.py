import pygame
import time
import signal
import json
import os
import threading
import paho.mqtt.client as mqtt

MQTT_TOPIC = "/band/vibration"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

pauza = 1
puls = 0.5
haptic_play_duration = 5

pygame.init()
pygame.mixer.init()

sound_file = os.path.join("Sounds", "vibrations.mp3")

pygame.mixer.music.load(sound_file)
pygame.mixer.music.set_volume(0.7)

def pulse():

    pygame.mixer.music.play(start = 0.5)
    time.sleep(pauza)

    pygame.mixer.music.stop()


def short_pause():
    time.sleep(0.5)
def pause():
    time.sleep(1)
def es_pause():
    time.sleep(0.25)

def short_pulse():

    pygame.mixer.music.play(start = 0.5)
    time.sleep(puls)

   # pygame.mixer.music.fadeout(2000)
    pygame.mixer.music.stop()

def lh_bpm():
    
    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        short_pulse()
        short_pause()



def lh_bpressure():

    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        pulse()
        es_pause()
        

def lh_bodytemp():

    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        short_pulse()
        es_pause()
        short_pulse()
        es_pause()
        pulse()
        short_pause()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    poruka = json.loads(msg.payload.decode())

    value = poruka["value"]

    if value == "lh_bpm":
        lh_bpm()
    elif value == "lh_bpressure":
        lh_bpressure()
    elif value == "lh_bodytemp":
        lh_bodytemp()
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
        
        