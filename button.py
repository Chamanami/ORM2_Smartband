from messages import TopicMessage
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import socket
import time



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

topic = "/band/data/button"

def simulate_button_pressed():
    user_input = input("Press Enter button")
    return user_input == ""

def simulate_button_depressed():

    data = False

    message = TopicMessage({
        'type': "publish",
        'name': "Button",
        'ip': socket.gethostname(),
        'topic': topic,
        'value': data
    })

    client.publish(topic, message.toJSON())
    print("Button depressed!")


def publish_data(client):
    

    while True:
        if simulate_button_pressed():
            data = True

            message = TopicMessage({
                'type': "publish",
                'name': "Button",
                'ip': socket.gethostname(),
                'topic': topic,
                'value': data
            })

            client.publish(topic, message.toJSON())
            print("Button pressed!")
            time.sleep(3)

            simulate_button_depressed() #sad button :'(

        else:
            break


if __name__ == "__main__":
    client = listen_for_notify()
    publish_data(client)
    client.disconnect()