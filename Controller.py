import paho.mqtt.client as mqtt
import time
import json
import sys
from messages import TopicMessage
import socket
from threading import Thread
import subprocess

def start_server():

    controller.server_alive = True
    while controller.server_alive:
        try:
            controller.ssdp_notify(controller)
            time.sleep(15) #notify svakih 15 sekundi
        except KeyboardInterrupt:
            print("Program was shut down with keyboard interrupt")
            exit()

def start_mosquitto_broker():

    try:
        subprocess.run(["mosquitto", "-d"])
        print("Mosquitto broker je pokrenut.")
    except Exception as e:
        print(e)



class Controller():

    def __init__(self):
        self.name = "Controller"
        self.server_alive = False
        self.connected = False
        self.broadcast_port = 50000
        self.mqtt_port = 50002
        self.receive_port = 50001
        self.ip = socket.gethostbyname(socket.gethostname())
        self.client = self.start_mqtt_client()
        self.MQTT_TOPICS = [("/band/data/temperature",), ("/band/data/BPM",), ("/band/data/blood_pressure",), ("/band/button/pressed",)]

        self.alive = {'alive': True, 'ip': self.ip, 'port' : 1883}
        self.alive_size = sys.getsizeof(self.alive)
        self.socket_broadcast = self.init_socket('0.0.0.0', self.broadcast_port, False)
        self.threads = []

        self.bpm_message = None
        self.button_message = None
        self.pressure_message = None
        self.temperature_message = None

    def on_connect(self,client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe(self.MQTT_TOPICS)

    def start_mqtt_client(self):

        client = mqtt.Client()
        client.on_message = on_message
        client.on_connect = self.on_connect
        client.on_connect_fail = fail
        client.on_disconnect = fail

        client.connect(self.ip, self.mqtt_port, 60)
        client.loop_start()
        return client



    def init_socket(self,ip,port):
        sock = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )
        sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((ip, port))

        return sock

    def start(self):

        print("")
        #Trenutno dummy funkcija, ovde ce se pokretati kontroler i sve njegove funkcionalnosti (controller main())
        #1.Prvo Controller sam treba da se poveze sa brokerom
        #2.Implementirati zasebne funkcije za primanje poruka sa MQTT i za publishovanje poruka na MQTT
        #3.Napraviti tako da threadovi konstantno azuriraju poruke vezane za svaki od vitalnih znakova
        #Te poruke se smestaju kao Json objekti u polja Controllera odakle zasebna "brain" nit moze da ih ocita i na osnovu toga publishuje potrebnu komandu
        #Ako je tip poruke subscribe pravi se nova nit, u protivnom se azuriraju podaci


    def ssdp_notify(self):

        #Funkcija koja ce svakih 20 sekundi da se oglasi putem multicast kanala kako bi senzori i aktuatori znali na koju IP adresu da se konektuju
        data = json.dumps(self.alive).encode()
        sent = self.socket_broadcast.sendto(data, (self.ip, self.broadcast_port))

if __name__ == "__main__":

    controller = Controller()
    controller.threads.append(Thread(target=start_mosquitto_broker, args=(), daemon=True))
    controller.threads[-1].start() #Pokretanje brokera
    controller.threads.append(Thread(target=start_server, args=(), daemon=True))
    controller.threads[-1].start() #Pokretanje servera i oglasavanje na kojoj adresi je broker
    
    controller.start()
