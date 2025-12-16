# network.py
import socket
import json
import sys

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 5555
        
        print("\n--- SUNUCU BAĞLANTISI ---")
        print("Sunucu bu bilgisayardaysa boş bırakıp ENTER'a basın.")
        server_ip = input("Sunucu IP Adresi (Örn: 192.168.1.35): ").strip()
        
        if not server_ip:
            self.server = "127.0.0.1"
        else:
            self.server = server_ip
            
        self.addr = (self.server, self.port)
        
        # Sunucuya bağlanmayı dene
        response = self.connect()
        
        if response is None:
             print("\n!!! HATA: Sunucuya bağlanılamadı !!!")
             print(f"Lütfen '{self.server}' IP adresinde 'server.py' dosyasının çalıştığından emin olun.\n")
             sys.exit() 
             
        self.player_id = int(response)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except socket.error as e:
            return None

    def send(self, data):
        try:
            self.client.send(str.encode(json.dumps(data)))
            return json.loads(self.client.recv(2048).decode())
        except socket.error as e:
            print(e)