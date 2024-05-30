from messages import TopicMessage
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading



def setup_mqtt_connection(broker_adress,broker_port):
    client = mqtt.Client()
    client.connect(broker_adress,broker_port)
    return client

def simulate_button_pressed():
    user_input = input("Press Enter button")
    return user_input == ""


if __name__ == "__main__":
    broker_adress = "localhost"  # TODO
    broker_port = 1883

    # topic for bpm values
    topic = "/band/data/button"

    client = setup_mqtt_connection(broker_adress, broker_port)

    while True:
        if simulate_button_pressed():
            data = True

            message = TopicMessage({
                'type': "publish",
                'name': "Button",
                'ip': "localhost",
                'topic': topic,
                'value': data
            })

            client.publish(topic, message.toJSON())

            print("Button pressed!")

            break

        client.disconnect()