# server.py
import socket
import threading
import json

# "0.0.0.0" demek, ağdaki tüm bilgisayarlardan gelen isteklere açığım demek.
HOST = '0.0.0.0'
PORT = 5555

clients = []
game_state = {"p1": {"x": 0, "y": 0}, "p2": {"x": 0, "y": 0}}

def get_local_ip():
    """Bilgisayarın ağdaki gerçek IP adresini bulur."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Google'ın DNS sunucusuna bağlanmayı deneyerek gerçek IP'yi öğreniriz
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def handle_client(conn, player_id):
    conn.send(str.encode(str(player_id))) # Oyuncuya kim olduğunu söyle (0 veya 1)
    
    while True:
        try:
            data = conn.recv(2048).decode()
            if not data:
                break
            
            # İstemciden gelen veriyi işle
            pos = json.loads(data)
            key = "p1" if player_id == 0 else "p2"
            game_state[key] = pos

            # Diğer oyuncunun konumunu geri gönder
            if player_id == 0:
                reply = game_state["p2"]
            else:
                reply = game_state["p1"]
                
            conn.sendall(str.encode(json.dumps(reply)))
            
        except:
            break
            
    print(f"Oyuncu {player_id} bağlantısı koptu.")
    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))

    s.listen(2)
    
    local_ip = get_local_ip()
    print("------------------------------------------------")
    print(f"Sunucu Başlatıldı! IP Adresiniz: {local_ip}")
    print("Diğer bilgisayardan bağlanırken bu IP'yi girin.")
    print("------------------------------------------------")
    print("Oyuncular bekleniyor...")

    current_player = 0
    while True:
        conn, addr = s.accept()
        print("Bağlandı:", addr)
        
        t = threading.Thread(target=handle_client, args=(conn, current_player))
        t.start()
        current_player += 1

if __name__ == "__main__":
    start_server()