import socket
import threading
import re

class client_address:

    def __init__(self, adresa, port):

        self.adresa = adresa
        self.port = port
    
    def getAddress(self):
        return str(self.adresa)
    def getPort(self):
        return int(self.port)


    
def handle_client(client_address):
    TCP_TIMEOUT = 10
    BUFFER_SIZE = 1024

    # Poveži se sa klijentom
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(TCP_TIMEOUT)
        client_socket.connect((client_address.getAddress(), client_address.getPort()))
    except socket.error as e:
        print(f"Greška prilikom povezivanja sa klijentom {client_address.getAddress()}:{client_address.getPort()}: {e}")
        return

    # Održavanje konekcije
    try:
        while True:
            
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break 
            
            
            print(f"Primljeno od klijenta {client_address.getAddress()}:{client_address.getPort()}: {data.decode()}")
    except socket.timeout:
        print(f"Konekcija sa klijentom {client_address.getAddress()}:{client_address.getPort()} je istekla (timeout).")
    except socket.error as e:
        print(f"Greška prilikom komunikacije sa klijentom {client_address.getAddress()}:{client_address.getPort()}: {e}")
    except KeyboardInterrupt as e:
        print("Prekid programa.")
    finally:
        client_socket.close()
        print(f"Konekcija sa klijentom {client_address.getAddress()}:{client_address.getPort()} je zatvorena.")


def discover_service():
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900
    TIMEOUT = 10 

    clients = []

    location_pattern = re.compile(r"LOCATION: ([\d\.]+):(\d+)\r\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", SSDP_PORT))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(SSDP_ADDR) + socket.inet_aton("0.0.0.0"))

    try:
        sock.settimeout(TIMEOUT)
        while (1):

            adresa = None
            port = None
            adresa_port = None

            data, addr = sock.recvfrom(1024)
            print("Received:", data.decode())

            try:
                adresa_port = location_pattern.search(data.decode())
                adresa = adresa_port.group(1)
                port = adresa_port.group(2)
            except AttributeError as e:
                print("")
                
                

            if adresa is not None and port is not None:    

                new_client = client_address(adresa, port)
                is_in_list = False

                for c in clients:

                    if c.getAddress() == new_client.getAddress():
                        is_in_list = True

                if not is_in_list:
                    clients.append(new_client)
                    client_thread = threading.Thread(target=handle_client, args=(new_client, ))
                    client_thread.start()

    except socket.timeout:
        print("Timeout reached. SSDP service not found.")
        return False

    return True

if __name__ == "__main__":

    multicast_thread = threading.Thread(target=discover_service())
    multicast_thread.start()

