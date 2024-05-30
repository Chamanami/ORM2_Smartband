import time
import random
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from messages import TopicMessage
import threading

#todo dodati za disconnect


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
    broker_adress = "localhost" #TODO
    broker_port = 1883

    #topic for bpm values
    topic ="/band/data/BPM"

    client = setup_mqtt_connection(broker_adress, broker_port)

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


