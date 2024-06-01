import time
import signal
import json
import socket
import paho.mqtt.client as mqtt
import soundfile as sf
import sounddevice as sd

MQTT_TOPIC = "/band/vibration"
MQTT_BROKER = None
MQTT_PORT = 1883


def signal_handler(sig, frame):
    print("Program je prekinut")
    exit()

signal.signal(signal.SIGINT, signal_handler)

def init_sock():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("239.255.255.250", 1900))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton("239.255.255.250") + socket.inet_aton("0.0.0.0"))
    return sock, True
    
def play_audio_with_limits(filename, start_seconds, duration_seconds):
   
    data, fs = sf.read(filename)

    start_sample = int(start_seconds * fs)
    duration_samples = int(duration_seconds * fs)

    data_to_play = data[start_sample:start_sample + duration_samples]

    sd.play(data_to_play, fs)
    sd.wait()

def listen_for_notify():

    connected = False
    init_succ = False

    while not init_succ:
        try:
            sock, init_succ = init_sock()
        except OSError:
            time.sleep(1)    

    while not connected:
        
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(message)


        try:
            message_data = json.loads(message)

            if 'alive' in message_data:

                broker_ip = message_data['ip']
                client = start_mqtt_subscriber(broker_ip)
                connected = True
                print("Connect request sent to broker")
                return client

        except json.JSONDecodeError:
            print("Json Decoding error")

pauza = 1
puls = 0.5
haptic_play_duration = 5
audio_file = "Sounds/vibrations.mp3"
start_time = 0.5
duration = 1

def pulse():
    
    play_audio_with_limits(audio_file, start_time, duration)


def short_pause():
    time.sleep(0.5)
def pause():
    time.sleep(1)
def es_pause():
    time.sleep(0.25)

def short_pulse():

    play_audio_with_limits(audio_file, start_time, puls)

def lh_bpm():
    
    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        short_pulse()
        short_pause()



def lh_bpressure():

    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        pulse()
        es_pause()
        

def lh_bodytemp():

    end_time = time.time() + haptic_play_duration

    while time.time() < end_time:
        short_pulse()
        es_pause()
        short_pulse()
        es_pause()
        pulse()
        short_pause()

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    poruka = json.loads(msg.payload.decode())

    value = poruka["value"]

    if value == "lh_bpm":
        lh_bpm()
    elif value == "lh_bpressure":
        lh_bpressure()
    elif value == "lh_bodytemp":
        lh_bodytemp()
    else:
        print("Unknown command received from the controller")

def fail(client, userdata, rc):
    print("CONNECTION FAILED")


def start_mqtt_subscriber(ip):
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_connect_fail = fail
    client.on_disconnect = fail

    client.connect(ip, MQTT_PORT, 60)
    client.loop_start()
    return client

if __name__ == "__main__":

    mqtt_client = listen_for_notify()
    signal.pause()
    
    
        
        