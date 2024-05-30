import random
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from messages import TopicMessage



def setup_mqtt_connection(broker_adress,broker_port):
    client = mqtt.Client()
    client.connect(broker_adress,broker_port)
    return client

def simulate_temperature(normal_range=(35,38), spike_range=(39,42), spike_probability = 0.5, interval = 1):

    while True:
        if random.random() < spike_probability:
            temperature = random.randint(*spike_range)
        else:
            temperature = random.randint(*normal_range)

        yield temperature
        time.sleep(interval)


if __name__ == "__main__":
    broker_adress = "localhost"  # TODO
    broker_port = 1883

    # topic for bpm values
    topic = "/band/data/temperature"

    client = setup_mqtt_connection(broker_adress, broker_port)

    # create a generator for simulating heart rate readings


    sensor = simulate_temperature()
    for _ in range(20):
        temperature = next(sensor)

        message = TopicMessage({
            'type': "publish",
            'name': "Temperature sensor",
            'ip': "localhost",
            'topic': topic,
            'value': temperature
        })

        client.publish(topic, message.toJSON())
        print(f"Temperature: {temperature} deg C")

        time.sleep(1)
    client.disconnect()

