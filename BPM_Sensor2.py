import json
import time
import random
import paho.mqtt.client as mqtt
from messages import TopicMessage
import socket
import signal

#todo dodati za disconnect

IP_ADDRESS_MULTICAST = '239.255.255.250'
PORT_MULTICAST = 1900

def signal_handler(sig,frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def listen_for_notify():

    binded = False

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    sock.bind(("239.255.255.250", 1900))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,socket.inet_aton("239.255.255.250") + socket.inet_aton("0.0.0.0"))





    connected = False

    while connected == False:
        data, adr = sock.recvfrom(1024)
        message = data.decode()

        try:
            message_data = json.loads(message)

            if 'alive' in message_data:
                broker_ip = message_data['ip']
                broker_port = message_data['port']
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




if __name__ == "__main__":
    #mqtt broker details
    #broker_adress = "localhost" #TODO
    #broker_port = 1883

    #topic for bpm values
    topic ="/band/data/BPM"

    #client = setup_mqtt_connection(broker_adress, broker_port)
    client = listen_for_notify()

    # create a generator for simulating heart rate readings
    sensor = simulate_heartbeat()

    for _ in range(20):  # Simulate 20 readings
        bpm = next(sensor)

        message = TopicMessage ({
            'type':"publish",
            'name':"BPM Sensor",
            'ip':"localhost",
            'topic':topic,
            'value_type': "int",
            'value':bpm
        })

        client.publish(topic,message.toJSON())

        print(f"Published Heart Rate: {bpm} BPM")

        time.sleep(1)

    client.disconnect()


