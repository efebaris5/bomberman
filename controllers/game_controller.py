import time
import random
from config import GRID_WIDTH, GRID_HEIGHT
from database import DatabaseRepository
from patterns.factories import ForestThemeFactory, CityThemeFactory, DesertThemeFactory
from patterns.strategies import AStarStrategy
from patterns.commands import MoveCommand, PlaceBombCommand
from patterns.decorators import BombPowerUp, BombCountPowerUp, SpeedPowerUp
from models.entities import Player, Enemy, Bomb, PowerUpItem
from network import Network
from sound_manager import SoundManager 

class GameController:
    def __init__(self, view, user_data):
        self.view = view
        self.repo = DatabaseRepository()
        self.sound_manager = SoundManager()
        self.main_app_ref = None 
        self.on_exit_callback = None 

        # user_data: (id, username, wins, losses, theme)
        self.user_id = user_data[0]
        self.username = user_data[1]
        self.wins = user_data[2]
        self.losses = user_data[3]
        self.theme_choice = user_data[4]
        
        self.last_killed_enemies = []
        self.net = Network()
        self.player_id = self.net.player_id
        
        # --- TEMA FABRİKASI ---
        if self.theme_choice == "City":
            self.factory = CityThemeFactory()
        elif self.theme_choice == "Desert":
            self.factory = DesertThemeFactory()
        else:
            self.factory = ForestThemeFactory()
            
        print(f"Aktif Tema: {self.theme_choice}")
        self.view.set_background(self.factory.get_background_color())
        
        self.grid_walls = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.powerups = []
        
        # 1. Önce Haritayı Oluştur (Seed olmadan!)
        self._generate_map()
        
        # 2. Oyuncu İçin Güvenli Rastgele Yer Bul
        px, py = self._find_safe_spawn()
        self.player = Player(px, py)
        
        # 3. Düşman İçin Uzak Bir Yer Bul (Oyuncudan en az 8 birim uzakta)
        ex, ey = self._find_safe_spawn(avoid_pos=(px, py), min_dist=8)
        self.enemies = [Enemy(ex, ey, AStarStrategy())]

        # Multiplayer rakibi (Şimdilik sabit köşede kalsın veya o da random olabilir)
        # Basitlik için rakibi sağ alt köşeye yakın güvenli bir yere koyalım
        self.opponent = Player(GRID_WIDTH-2, GRID_HEIGHT-2) 

        self.bombs = []
        self.explosions = []
        self.running = True
        self.last_action = None
        
        self.view.bind_keys(self.handle_input)
        self.update_score_ui()
        self.game_loop()

    def _generate_map(self):
        # random.seed(12345)  <-- BU SATIRI SİLDİK! Artık her oyun farklı.
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Çerçeve (Kırılmaz Duvarlar)
                if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                # İçerdeki Direkler (Kırılmaz Duvarlar)
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                else:
                    # Rastgele Kırılabilir Duvarlar
                    if random.random() < 0.4: # %40 ihtimalle duvar
                        if random.random() < 0.15:
                            self.grid_walls[y][x] = self.factory.create_durable_wall()
                        else:
                            self.grid_walls[y][x] = self.factory.create_soft_wall()

    def _find_safe_spawn(self, avoid_pos=None, min_dist=0):
        """Güvenli, duvar olmayan ve (varsa) hedeften uzak bir koordinat bulur."""
        while True:
            # Rastgele bir koordinat seç (Çerçeveler hariç)
            c = random.randint(1, GRID_WIDTH - 2)
            r = random.randint(1, GRID_HEIGHT - 2)
            
            # 1. Kural: Seçilen yer 'Sert Duvar' (Hard Wall) olamaz
            wall = self.grid_walls[r][c]
            if wall and not wall.is_breakable():
                continue
                
            # 2. Kural: Eğer birinden uzak durulması gerekiyorsa mesafeyi ölç
            if avoid_pos:
                dist = abs(c - avoid_pos[0]) + abs(r - avoid_pos[1])
                if dist < min_dist:
                    continue # Çok yakın, tekrar dene
            
            # 3. Kural: Seçilen yer uygunsa, oradaki (varsa) yumuşak duvarı sil
            # Böylece oyuncu veya düşman duvarın içine doğmaz.
            self.grid_walls[r][c] = None
            
            # İsteğe bağlı: Oyuncunun sıkışmaması için etrafındaki 1-2 duvarı da silebiliriz
            # Şimdilik sadece doğduğu kareyi temizlemek yeterli.
            
            return c, r

    def update_score_ui(self):
        stats_text = f"PLAYER: {self.username}\nWINS: {self.wins} | LOSSES: {self.losses}\nTHEME: {self.theme_choice}"
        if hasattr(self.view, 'info_label'):
             self.view.info_label.config(text=stats_text)

    def handle_input(self, key):
        if not self.running: return
        
        command = None
        if key == 'Up': 
            command = MoveCommand(self.player, 0, -1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT, on_step_callback=self.check_powerups)
        elif key == 'Down': 
            command = MoveCommand(self.player, 0, 1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT, on_step_callback=self.check_powerups)
        elif key == 'Left': 
            command = MoveCommand(self.player, -1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT, on_step_callback=self.check_powerups)
        elif key == 'Right': 
            command = MoveCommand(self.player, 1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT, on_step_callback=self.check_powerups)
        elif key == 'space': 
            command = PlaceBombCommand(self)
        elif key == 'Escape': 
            self.running = False; self.view.parent.quit()

        if command:
            command.execute()
            self.check_powerups()

    def check_powerups(self):
        for p in self.powerups:
            if p.active and p.x == self.player.x and p.y == self.player.y:
                p.active = False
                self.sound_manager.play_sound("POWERUP")
                choice = random.choice(["power", "count", "speed"])
                if choice == "power": self.player = BombPowerUp(self.player)
                elif choice == "count": self.player = BombCountPowerUp(self.player)
                elif choice == "speed": self.player = SpeedPowerUp(self.player)
                print(f"Güçlendirme alındı: {choice}")
                
    def place_bomb(self):
        my_active_bombs = [b for b in self.bombs if not b.exploded]
        if len(my_active_bombs) < self.player.get_max_bombs():
            bomb = Bomb(self.player.x, self.player.y, self.player.get_bomb_power())
            bomb.add_observer(self.player) 
            bomb.add_observer(self.opponent)
            for enemy in self.enemies:
                bomb.add_observer(enemy)
            self.bombs.append(bomb)
            self.last_action = "BOMB"
            self.sound_manager.play_sound("BOMB")

    def game_over(self, result):
        if not self.running: return
        self.running = False
        
        is_win = (result == "WIN")
        self.repo.update_stats(self.username, is_win)
        
        if is_win:
            self.sound_manager.play_sound("WIN")
            msg, color = "KAZANDIN!", "#4CAF50"
        else:
            self.sound_manager.play_sound("LOSE")
            msg, color = "KAYBETTİN!", "#F44336"
            
        self.view.show_game_over(msg, color)

    def on_game_over_menu(self):
        self.running = False
        if self.on_exit_callback:
            self.on_exit_callback()

    def game_loop(self):
        if not self.running: return
        current_time = time.time() * 1000
        current_time_sec = time.time() # Saniye cinsinden zaman (Patlama süresi için)
        
        # --- AĞ ve OYUNCU KONTROLLERİ (Aynı kalıyor) ---
        try:
            my_data = {
                "x": self.player.x, "y": self.player.y, 
                "alive": self.player.is_alive, "action": self.last_action,
                "killed_enemies": self.last_killed_enemies
            }
            reply = self.net.send(my_data)
            self.last_action = None
            self.last_killed_enemies = [] 
            
            if reply:
                self.opponent.set_pos(reply["x"], reply["y"])
                if "action" in reply and reply["action"] == "BOMB":
                    opp_bomb = Bomb(self.opponent.x, self.opponent.y, 1)
                    opp_bomb.add_observer(self.player)
                    self.bombs.append(opp_bomb)
                    self.sound_manager.play_sound("BOMB")
                if "killed_enemies" in reply:
                    for enemy_idx in reply["killed_enemies"]:
                        if enemy_idx < len(self.enemies) and self.enemies[enemy_idx].is_alive:
                            self.enemies[enemy_idx].is_alive = False
                if "alive" in reply and not reply["alive"] and self.player.is_alive:
                    self.game_over("WIN")
                    return
        except Exception:
            pass

        if not self.player.is_alive:
            self.game_over("LOSE")
            return

        # --- PATLAMALARI VE BOMBALARI YÖNETME (GÜNCELLENDİ) ---
        bombs_to_remove = []
        for bomb in self.bombs:
            explosion_area = bomb.check_explosion(current_time, GRID_WIDTH, GRID_HEIGHT, self.grid_walls)
            if explosion_area:
                bombs_to_remove.append(bomb)
                self.sound_manager.play_sound("EXPLOSION")
                
                # --- YENİ: Patlamayı listeye ekle (0.5 saniye ekranda kalsın) ---
                self.explosions.append({
                    "area": explosion_area,
                    "end_time": current_time_sec + 0.5 
                })
                
                # Duvarları kırma ve Düşman öldürme mantığı
                for (ex, ey) in explosion_area:
                    wall = self.grid_walls[ey][ex]
                    if wall and wall.is_breakable():
                        if hasattr(wall, 'take_damage'):
                            if wall.take_damage(): self.grid_walls[ey][ex] = None
                        else:
                            self.grid_walls[ey][ex] = None
                            if random.random() < 0.3: self.powerups.append(PowerUpItem(ex, ey))
                    
                    for idx, enemy in enumerate(self.enemies):
                        if enemy.is_alive and enemy.x == ex and enemy.y == ey:
                            enemy.is_alive = False
                            self.last_killed_enemies.append(idx)
                            
                    # Kendini vurma kontrolü (Can sistemi varsa)
                    if self.player.x == ex and self.player.y == ey:
                         if hasattr(self.player, 'take_damage'):
                            self.player.take_damage()
                         else:
                            self.player.kill()

        for b in bombs_to_remove: self.bombs.remove(b)

        # --- SÜRESİ BİTEN PATLAMALARI SİL ---
        self.explosions = [exp for exp in self.explosions if exp["end_time"] > current_time_sec]

        # --- OYUN MANTIĞI DEVAMI ---
        active_enemies = [e for e in self.enemies if e.is_alive]
        if not active_enemies and self.player.is_alive:
             self.game_over("WIN")
             return

        if int(time.time() * 10) % 5 == 0:
            for enemy in self.enemies:
                if enemy.is_alive:
                    enemy.move((self.player.x, self.player.y), self.grid_walls)
                    if enemy.x == self.player.x and enemy.y == self.player.y:
                        if hasattr(self.player, 'take_damage'):
                            self.player.take_damage()
                        else:
                            self.player.kill()

        # --- ÇİZİM (GÜNCELLENDİ: patlamalar da gönderiliyor) ---
        all_entities = self.enemies + [self.opponent]
        
        # draw fonksiyonuna self.explosions listesini de gönderiyoruz
        self.view.draw(self.grid_walls, self.player, all_entities, self.bombs, self.powerups, self.explosions)
        
        self.view.after(50, self.game_loop)