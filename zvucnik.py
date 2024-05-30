import pygame
import time
import paho.mqtt.client as mqtt
import signal
import socket
import json
import threading
import os

MQTT_TOPIC = "/band/sound"
MQTT_BROKER = None
MQTT_PORT = 1883
connected = False

def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def listen_for_notify():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("239.255.255.250", 150))

    while connected == False:
        
        data, addr = sock.recvfrom(1024)
        message = data.decode()


        try:
            message_data = json.loads(message)

            if 'alive' in message_data:

                broker_ip = message_data['ip']
                client = start_mqtt_subscriber(broker_ip)
                connected = True
                print("Connect request sent to broker")
                return client

        except json.JSONDecodeError:
            print("Json Decoding error")


        

def func():
    time_to_play = 5
    pauza = 0.75

    pygame.init()
    pygame.mixer.init()

    sound_file = os.path.join("Sounds", "pomoc.mp3")

    pygame.mixer.music.load(sound_file)

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


def start_mqtt_subscriber(ip):
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_connect_fail = fail
    client.on_disconnect = fail

    client.connect(ip, MQTT_PORT, 60)
    client.loop_start()
    return client

if __name__ == "__main__":

    mqtt_client = listen_for_notify()
    
    signal.pause()