import paho.mqtt.client as mqtt
import time
import json
import signal
import sys
from messages import TopicMessage
import socket
from threading import Thread
import subprocess

BPsys_low = 90
BPsys_hi = 140
BPdia_hi = 90

BPMhi = 100
BPMlow = 60

Temphi = 38
Templow = 35

def start_server():

    controller.server_alive = True
    while controller.server_alive:
        try:
            controller.ssdp_notify()
            time.sleep(5) #notify svakih 15 sekundi
        except KeyboardInterrupt:
            print("Program was shut down with keyboard interrupt")
            exit()

def start_mosquitto_broker():

    try:
        
        subprocess.run(["mosquitto","-d"], check=True)
        print("Mosquitto broker je pokrenut.")
    except Exception as e:
        print(e)

def signal_handler(sig, frame):
        print("Program je prekinut")
        exit()

class Controller():

    def __init__(self):
        self.name = "Controller"
        self.server_alive = False
        self.connected = False
        self.broadcast_port = 1900
        self.mqtt_port = 1883
        self.receive_port = 50001
        self.ip = socket.gethostbyname('localhost')
        self.client = None
        self.MQTT_TOPICS = [("/band/data/temperature",0), ("/band/data/BPM",0), ("/band/data/blood_pressure",0), ("/band/data/button",0)]

        self.alive = {'alive': True, 'ip': self.ip, 'port' : 1883}
        self.alive_size = sys.getsizeof(self.alive)
        self.socket_broadcast = self.init_socket('239.255.255.250', self.broadcast_port)
        self.threads = []

        self.bpm_message = None
        self.button_message = None
        self.pressure_message = None
        self.temperature_message = None

        self.BPM = None
        self.button = None
        self.pressure = None
        self.pressure_sys = None
        self.pressure_dia = None
        self.temperature = None

        signal.signal(signal.SIGINT, signal_handler)

    def on_connect(self,client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe(self.MQTT_TOPICS)
    
    def on_message(self, client, userdata, msg):

        message = json.loads(msg.payload.decode())

        category = message["topic"].split("/")[3]

        if category == "temperature":
            self.temperature_message = message
            self.temperature = message["value"]
        elif category == "BPM":
            self.bpm_message = message
            self.BPM = message["value"]
        elif category == "blood_pressure":
            self.pressure_message = message
            self.pressure = message["value"]
            delovi = self.pressure.split("/")
            self.pressure_dia = delovi[1]
            self.pressure_sys = delovi[0]
        elif category == "button":
            self.button_message = message
            self.button = message["value"]
        else:
            print("Unknown data received")


    def fail(client, userdata, rc):
        print("CONNECTION FAILED")


    def brain(self):

        #definisati logiku kontrolera
        while True:

            if self.temperature > Temphi or self.temperature < Templow:

                message = TopicMessage ({
            'type':"publish",
            'name':"Controller",
            'ip':self.ip,
            'topic':"/band/vibration",
            'value_type': "str",
            'value':"lh_bodytemp"
        })

                self.client.publish("/band/vibration",message.toJSON())

                print(f"Sent a command to the vibration motor, lh_bodytemp")

        



    def start_mqtt_client(self):

        client = mqtt.Client()
        client.on_message = self.on_message
        client.on_connect = self.on_connect
        client.on_connect_fail = self.fail
        client.on_disconnect = self.fail

        client.connect(self.ip, self.mqtt_port, 60)
        client.loop_start()
        return client



    def init_socket(self,ip,port):
        sock = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )
        sock.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_TTL, 2)

        return sock
    

    def start(self):

        #Trenutno dummy funkcija, ovde ce se pokretati kontroler i sve njegove funkcionalnosti (controller main())
 
        #2.Implementirati zasebne funkcije  za publishovanje poruka na MQTT

        self.client = self.start_mqtt_client()

        self.threads.append(Thread(target=self.brain(), args=(), daemon=True))
        self.threads[-1].start() #Pokretanje mozga kontrolera
        signal.pause()


    def ssdp_notify(self):

        #Funkcija koja ce svakih 20 sekundi da se oglasi putem multicast kanala kako bi senzori i aktuatori znali na koju IP adresu da se konektuju
        data = json.dumps(self.alive).encode()
        sent = self.socket_broadcast.sendto(data, ("239.255.255.250",self.broadcast_port))
        print(data)

if __name__ == "__main__":

    controller = Controller()
    controller.threads.append(Thread(target=start_mosquitto_broker, args=(), daemon=False))
    controller.threads[-1].start() #Pokretanje brokera
    time.sleep(2)
    controller.threads.append(Thread(target=start_server, args=(), daemon=True))
    controller.threads[-1].start() #Pokretanje servera i oglasavanje na kojoj adresi je broker
    time.sleep(5)
    controller.start()
