# controllers/game_controller.py
import time
import random
import json
from patterns.strategies import RandomStrategy, AStarStrategy
from config import GRID_WIDTH, GRID_HEIGHT
from database import DatabaseRepository
from patterns.factories import ForestThemeFactory, CityThemeFactory, DesertThemeFactory
from patterns.strategies import RandomStrategy
from patterns.decorators import BombPowerUp
from models.entities import Player, Enemy, Bomb, PowerUpItem
from network import Network
from patterns.commands import MoveCommand, PlaceBombCommand
from patterns.decorators import BombPowerUp, BombCountPowerUp, SpeedPowerUp

class GameController:
    def __init__(self, view, user_data):
        self.view = view
        self.repo = DatabaseRepository()
        
        self.user_id = user_data[0]
        self.username = user_data[1]
        self.wins = user_data[2]
        self.losses = user_data[3]
        self.last_killed_enemies = []
        
        self.net = Network()
        self.player_id = self.net.player_id
        
        
       # --- TEMA SEÇİMİ (Veritabanından) ---
        # Login_user artık 5. eleman olarak theme dönüyor (index 4)
        try:
            user_theme = user_data[4]
        except IndexError:
            user_theme = "Forest" # Eski veritabanı kalıntısı varsa hata almamak için

        if user_theme == "City":
            self.factory = CityThemeFactory()
        elif user_theme == "Desert":
            self.factory = DesertThemeFactory()
        else:
            self.factory = ForestThemeFactory() # Varsayılan
            
        print(f"Kullanıcı Teması Yüklendi: {user_theme}")
        self.view.set_background(self.factory.get_background_color())
        
        self.grid_walls = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.powerups = []
        self._generate_map()
        
        if self.player_id == 0:
            self.player = Player(1, 1)
            self.opponent = Player(13, 11)
        else:
            self.player = Player(13, 11)
            self.opponent = Player(1, 1)

        self.enemies = [Enemy(11, 9, AStarStrategy())]
        self.bombs = []
        self.running = True
        self.last_action = None
        
        self.view.bind_keys(self.handle_input)
        self.update_score_ui()
        self.game_loop()

    def update_score_ui(self):
        stats_text = f"{self.username} (W:{self.wins}/L:{self.losses})"
        self.view.info_label.config(text=f"{stats_text} | High Score: {self.repo.get_highscore()}")

    def _generate_map(self):
        random.seed(12345) # Harita senkronizasyonu için
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Çerçeve ve Sabit Bloklar
                if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                
                # Rastgele Duvarlar
                elif random.random() < 0.35 and not ((x<3 and y<3) or (x>11 and y>9)):
                    # %10 ihtimalle SERT DUVAR, %90 ihtimalle NORMAL DUVAR
                    if random.random() < 0.15:
                        self.grid_walls[y][x] = self.factory.create_durable_wall()
                    else:
                        self.grid_walls[y][x] = self.factory.create_soft_wall()

    def handle_input(self, key):
        command = None
        
        # Tuşa göre komut nesnesi oluşturuyoruz (Command Pattern)
        if key == 'Up':
            command = MoveCommand(self.player, 0, -1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Down':
            command = MoveCommand(self.player, 0, 1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Left':
            command = MoveCommand(self.player, -1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Right':
            command = MoveCommand(self.player, 1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'space':
            command = PlaceBombCommand(self)

        # Komutu çalıştır
        if command:
            command.execute()
            self.check_powerups() # Hareket sonrası power-up kontrolü
    def check_powerups(self):
        for p in self.powerups:
            if p.active and p.x == self.player.x and p.y == self.player.y:
                p.active = False
                
                # Rastgele bir güçlendirme seç
                choice = random.choice(["power", "count", "speed"])
                
                if choice == "power":
                    self.player = BombPowerUp(self.player)
                    print("Güçlendirme: Bomba Menzili Arttı!")
                elif choice == "count":
                    self.player = BombCountPowerUp(self.player)
                    print("Güçlendirme: Bomba Hakkı Arttı!")
                elif choice == "speed":
                    self.player = SpeedPowerUp(self.player)
                    print("Güçlendirme: Hız Arttı (Sembolik)!")
                
    def place_bomb(self):
        # Oyuncunun aktif bombalarını say (PlayerId kontrolü gerekebilir ama şimdilik basit tutuyoruz)
        # Basit mantık: Ekranda oyuncunun oluşturduğu patlamamış bomba sayısı
        my_active_bombs = [b for b in self.bombs if not b.exploded]
        
        if len(my_active_bombs) < self.player.get_max_bombs():
            bomb = Bomb(self.player.x, self.player.y, self.player.get_bomb_power())
            bomb.add_observer(self.player) 
            bomb.add_observer(self.opponent)
            self.bombs.append(bomb)
            self.last_action = "BOMB"
        else:
            print("Maksimum bomba sayısına ulaştınız!")

    def game_over(self, result):
        if not self.running: return
        self.running = False
        is_win = (result == "WIN")
        self.repo.update_stats(self.username, is_win)
        msg = "KAZANDIN!" if is_win else "KAYBETTİN!"
        color = "green" if is_win else "red"
        self.view.show_game_over(msg, color)

    # controllers/game_controller.py -> game_loop metodu

def game_loop(self):
    if not self.running: return
    current_time = time.time() * 1000
    
    # -------------------------------------------------------------
    # 1. AĞ SENKRONİZASYONU (Önce veriyi gönder, sonra işlem yap)
    # -------------------------------------------------------------
    try:
        my_data = {
            "x": self.player.x, 
            "y": self.player.y, 
            "alive": self.player.is_alive, # Ölüysek False gidecek
            "action": self.last_action,    # Bomba koyma bilgisi
            "killed_enemies": self.last_killed_enemies # [YENİ] Öldürdüğümüz düşmanlar
        }
        
        reply = self.net.send(my_data)
        
        # Gönderilen aksiyonları sıfırla (tekrar tekrar gitmesin)
        self.last_action = None
        self.last_killed_enemies = [] 

        if reply:
            # Rakibin Konumunu Güncelle
            self.opponent.set_pos(reply["x"], reply["y"])
            
            # [YENİ] Rakip Bomba Koydu mu?
            if "action" in reply and reply["action"] == "BOMB":
                # Rakibin bombasını kendi ekranımızda oluşturuyoruz
                opp_bomb = Bomb(self.opponent.x, self.opponent.y, 1)
                opp_bomb.add_observer(self.player) # Bu bomba bize zarar verebilir
                self.bombs.append(opp_bomb)
            
            # [YENİ] Rakip Bir Düşmanı Öldürdü mü?
            if "killed_enemies" in reply:
                for enemy_idx in reply["killed_enemies"]:
                    # Eğer indeks geçerliyse ve düşman hala yaşıyorsa öldür
                    if enemy_idx < len(self.enemies) and self.enemies[enemy_idx].is_alive:
                        self.enemies[enemy_idx].is_alive = False
                        # Görsel olarak da güncellemek istersen burada işlem yapabilirsin

            # Kazanma Kontrolü (Rakip ölmüşse kazanırız)
            if "alive" in reply and not reply["alive"] and self.player.is_alive:
                self.game_over("WIN")
                return
    except Exception as e:
        print(f"Ağ Hatası: {e}")

    # -------------------------------------------------------------
    # 2. ÖLÜM KONTROLÜ (Mesaj gönderildikten SONRA kontrol et)
    # -------------------------------------------------------------
    # Eğer bu turda ölü olduğumuz bilgisini gönderdiysek, şimdi oyunu bitirebiliriz.
    # Bu kontrolü 'send' işleminden SONRA yaparak karşı tarafa "öldüm" bilgisinin gitmesini garantiledik.
    if not self.player.is_alive:
        self.game_over("LOSE")
        return

    # -------------------------------------------------------------
    # 3. OYUN MANTIĞI (Patlamalar ve Düşmanlar)
    # -------------------------------------------------------------
    bombs_to_remove = []
    for bomb in self.bombs:
        explosion_area = bomb.check_explosion(current_time, GRID_WIDTH, GRID_HEIGHT, self.grid_walls)
        if explosion_area:
            bombs_to_remove.append(bomb)
            self.view.show_explosion(explosion_area)
            
            # Patlama alanındaki duvarları ve düşmanları kontrol et
            for (ex, ey) in explosion_area:
                # Duvar Kontrolü
                wall = self.grid_walls[ey][ex]
                if wall and wall.is_breakable():
                    if hasattr(wall, 'take_damage'):
                        if wall.take_damage():
                            self.grid_walls[ey][ex] = None
                            self.repo.save_score(self.repo.get_highscore() + 20)
                    else:
                        self.grid_walls[ey][ex] = None
                        self.repo.save_score(self.repo.get_highscore() + 10)
                        if random.random() < 0.3:
                            self.powerups.append(PowerUpItem(ex, ey))
                
                # [YENİ] Düşman Kontrolü (Patlamada Düşman Ölümü)
                for idx, enemy in enumerate(self.enemies):
                    if enemy.is_alive and enemy.x == ex and enemy.y == ey:
                        enemy.is_alive = False # Düşman öldü
                        self.last_killed_enemies.append(idx) # [YENİ] Ağa bildirilecek listeye ekle
                        print("Düşman patlamada öldü!")

    for b in bombs_to_remove: self.bombs.remove(b)

    # Düşman Hareketi
    if int(time.time() * 10) % 5 == 0:
        for enemy in self.enemies:
            if enemy.is_alive: # Sadece yaşayanlar hareket etsin
                enemy.move((self.player.x, self.player.y), self.grid_walls)
                if enemy.x == self.player.x and enemy.y == self.player.y:
                    self.player.kill()

    # -------------------------------------------------------------
    # 4. ÇİZİM VE DÖNGÜ
    # -------------------------------------------------------------
    all_entities = self.enemies + [self.opponent]
    self.view.draw(self.grid_walls, self.player, all_entities, self.bombs, self.powerups)
    
    # Döngüyü devam ettir (Artık player.is_alive kontrolü yukarıda yapılıyor)
    self.view.root.after(50, self.game_loop)