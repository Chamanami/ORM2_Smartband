import time
import random
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from messages import TopicMessage
import threading
import socket
import signal
import json

#todo dodati za disconnect

def signal_handler(sig,frame):
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



def simulate_heartbeat(base_range=(60,100), spike_range=(120,200),spike_probability = 0.3, interval=1):

    while True:
        if random.random() < spike_probability: #ako je float generisan random random manji od verov spajka, spajk se desava
            bpm = random.randint(*spike_range)
        else:
            bpm = random.randint(*base_range)

        yield bpm
        time.sleep(interval)

def setup_mqtt_connection(broker_adress,broker_port):
    client = mqtt.Client()
    client.connect(broker_adress,broker_port)
    return client



def publish_data(client):
    # create a generator for simulating heart rate readings
    sensor = simulate_heartbeat()
    topic = "/band/data/BPM"

    for _ in range(20):  # Simulate 20 readings
        bpm = next(sensor)

        message = TopicMessage({
            'type': "publish",
            'name': "BPM Sensor",
            'ip': socket.gethostname(),
            'topic': topic,
            'value_type': "int",
            'value': bpm
        })

        client.publish(topic, message.toJSON())

        print(f"Published Heart Rate: {bpm} BPM")

        time.sleep(1)




if __name__ == "__main__":


    client = listen_for_notify()

    publish_data(client)


    client.disconnect()

