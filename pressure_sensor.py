import random
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
from messages import TopicMessage



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


if __name__ == "__main__":
    broker_adress = "localhost"  # TODO
    broker_port = 1883

    # topic for bpm values
    topic = "/band/data/blood_pressure"

    client = setup_mqtt_connection(broker_adress, broker_port)

    # create a generator for simulating heart rate readings

    sensor = simulate_pressure()
    for _ in range(20):
        systolic,diastolic = next(sensor)

        pressure_string = "" + str(systolic) + "/" + str(diastolic)

        message = TopicMessage({
            'type': "publish",
            'name': "Blood Pressure Sensor",
            'ip': "localhost",
            'topic': topic,
            'value': pressure_string
        })

        client.publish(topic, message.toJSON())

        print(f"Blood Pressure: {systolic}/{diastolic} mmHg")

        time.sleep(1)

    client.disconnect()