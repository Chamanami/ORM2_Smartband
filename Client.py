import socket
import time
import sys
import threading

def handle_connections():
    SSDP_ADDR = "0.0.0.0"  
    SSDP_PORT = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SSDP_ADDR, SSDP_PORT))
    server_socket.listen(1)  # Prihvati maksimalno jednu konekciju

    while True:
        print("Čekanje na TCP zahtev...")
        client_socket, client_address = server_socket.accept()
        print(f"Zahtev prihvacen: {client_address}")
        
        # Održavanje TCP konekcije
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break  
                
               
                print(f"Primljeno od klijenta {client_address}: {data.decode()}")
        except Exception as e:
            print(f"Greška prilikom komunikacije sa klijentom {client_address}: {e}")
        except KeyboardInterrupt as e:
            print("Prekid programa.")
            server_socket.close()
            sys.exit()
        finally:
            # Zatvaranje TCP konekcije
            client_socket.close()
            print(f"Konekcija sa klijentom {client_address} je zatvorena.")
            return

def advertise_service():
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900
    SSDP_MX = 1
    ST = "discovery_service"
    UUID = 12345

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    message = (
        "NOTIFY * HTTP/1.1\r\n"
        "HOST: {address}:{port}\r\n"
        "NT: {st}\r\n"
        "NTS: ssdp:alive\r\n"
        "LOCATION: {location}\r\n"
        "CACHE-CONTROL: max-age={max_age}\r\n"
        "SERVER: RT_RK waf\r\n"
    ).format(
        address=SSDP_ADDR,
        port=SSDP_PORT,
        st=ST,
        location="{}:{}".format(socket.gethostbyname(socket.gethostname()), 5000), 
        max_age=SSDP_MX,
    )

    byebye = (
        "NOTIFY * HTTP/1.1\r\n"
        "HOST: {address}:{port}\r\n"
        "NT: {st}\r\n"
        "NTS: ssdp:byebye\r\n"
        "USN: {usn}\r\n"
    ).format(
        address=SSDP_ADDR,
        port=SSDP_PORT,
        st=ST,
        usn="{}::{}".format(UUID, ST),
    )

    m_search = (
        "M-SEARCH * HTTP/1.1\r\n"
        "HOST: {address}:{port}\r\n"
        "MAN: \"ssdp:discover\"\r\n"
        "ST: {st}\r\n"
        "MX: 1\r\n"
    ).format(
        address=SSDP_ADDR,
        port=SSDP_PORT,
        st=ST,
    )

    try:
        sock.sendto(m_search.encode(), (SSDP_ADDR, SSDP_PORT))
        while True:

            sock.sendto(message.encode(), (SSDP_ADDR, SSDP_PORT))
            print("Veza uspostavljena: True")
            time.sleep(10)  # Pauza od 10 sekundi između objava
            
    except Exception as e:
        print("Greška prilikom slanja poruke:", str(e))
        return False
    except KeyboardInterrupt as e:
        sock.sendto(byebye.encode(), (SSDP_ADDR, SSDP_PORT)) # Slanje byebye poruke na gasenje programa (KeyboardInterrupt)
        print("Prekid programa.")
        sock.close()
        sys.exit()

if __name__ == "__main__":

    connections_thread = threading.Thread(target=handle_connections)
    connections_thread.start()

    multicast_thread = threading.Thread(target=advertise_service)
    multicast_thread.start()
