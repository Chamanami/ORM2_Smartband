import random
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from messages import TopicMessage
import threading
import socket
import json



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

def simulate_temperature(normal_range=(35,38), spike_range=(39,42), spike_probability = 0.05, interval = 1):

    while True:
        if random.random() < spike_probability:
            temperature = random.randint(*spike_range)
        else:
            temperature = random.randint(*normal_range)

        yield temperature
        time.sleep(interval)


def publish_data(client):
    topic = "/band/data/temperature"

    sensor = simulate_temperature()
    while True:
        temperature = next(sensor)

        message = TopicMessage({
            'type': "publish",
            'name': "Temperature sensor",
            'ip': socket.gethostname(),
            'topic': topic,
            'value': temperature
        })

        client.publish(topic, message.toJSON())
        print(f"Temperature: {temperature} deg C")

        time.sleep(1)



if __name__ == "__main__":
    client = listen_for_notify()
    publish_data(client)
    client.disconnect()
