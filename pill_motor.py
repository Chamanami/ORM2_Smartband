import signal
import json
import time
import paho.mqtt.client as mqtt
import socket
import re
import threading

MQTT_TOPIC = "/band/meds_dispenser"
MQTT_BROKER = None
MQTT_PORT = 1883


open = False


def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def init_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("239.255.255.250", 1900))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton("239.255.255.250") + socket.inet_aton("0.0.0.0"))
    return sock, True

def listen_for_notify():

    connected = False

    init_succ = False

    while not init_succ:
        try:
            sock, init_succ = init_sock()
        except OSError:
            time.sleep(1)
    

    while not connected:
        
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(message)

        try:
            message_data = json.loads(message)

            alive = message_data['alive']

            if alive:

                broker_ip = message_data['ip']
                client = start_mqtt_subscriber(broker_ip)
                connected = True
                print("Connect request sent to broker")
                return client

        except json.JSONDecodeError:
            print("Json Decoding error")

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