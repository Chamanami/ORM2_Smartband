import random
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import socket
import json
from messages import TopicMessage

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
            sock,init_succ = init_sock()
        except OSError:
            time.sleep(1)

    while connected == False:
        data, adr = sock.recvfrom(1024)
        message = data.decode()

        try:
            message_data = json.loads(message)
            if 'alive' in message_data:
                broker_ip = message_data['ip']
                client = setup_mqtt_connection(broker_ip,1883)
                connected = True
                print("Connect request sent to broker")
                return client

        except json.JSONDecodeError:
            print("Json Decoding Error")


def setup_mqtt_connection(broker_adress,broker_port):
    client = mqtt.Client()
    client.connect(broker_adress,broker_port)
    return client


def simulate_pressure(systolic_range=(90,120), diastolic_range=(60,80),
                     spike_range_systolic=(140,180), spike_range_diastolic=(90,110),
                    spike_probability=0.05,interval=1):

    while True:
        if random.random() < spike_probability:
            systolic = random.randint(*spike_range_systolic)
            diastolic = random.randint(*spike_range_diastolic)
        else:
            systolic = random.randint(*systolic_range)
            diastolic = random.randint(*diastolic_range)

        yield systolic,diastolic
        time.sleep(interval)


def publish_data(client):
    sensor = simulate_pressure()
    topic = "/band/data/blood_pressure"

    for _ in range(20):
        systolic, diastolic = next(sensor)
        pressure_string = "" + str(systolic) + "/" + str(diastolic)

        message = TopicMessage({
            'type': "publish",
            'name': "Blood Pressure Sensor",
            'ip': socket.gethostname(),
            'topic': topic,
            'value': pressure_string
        })

        client.publish(topic, message.toJSON())
        print(f"Blood Pressure: {systolic}/{diastolic} mmHg")
        time.sleep(1)



if __name__ == "__main__":
    client = listen_for_notify()
    publish_data(client)
    client.disconnect()