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

class GameController:
    def __init__(self, view, user_data):
        self.view = view
        self.repo = DatabaseRepository()
        
        # user_data: (id, username, wins, losses, theme)
        self.user_id = user_data[0]
        self.username = user_data[1]
        self.wins = user_data[2]
        self.losses = user_data[3]
        self.theme_choice = user_data[4] # Veritabanından gelen tema
        
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
        self._generate_map()
        
        # Oyuncu Konumları
        if self.player_id == 0:
            self.player = Player(1, 1)
            self.opponent = Player(13, 11)
        else:
            self.player = Player(13, 11)
            self.opponent = Player(1, 1)

        # Düşman (Bot) Ekleme
        self.enemies = [Enemy(11, 9, AStarStrategy())]
        self.bombs = []
        self.running = True
        self.last_action = None
        
        self.view.bind_keys(self.handle_input)
        self.update_score_ui()
        self.game_loop()

    def update_score_ui(self):
        # Sağ paneldeki info label'ı güncelle
        stats_text = f"PLAYER: {self.username}\nWINS: {self.wins} | LOSSES: {self.losses}\nTHEME: {self.theme_choice}"
        # Eğer view'da info_label varsa güncelle
        if hasattr(self.view, 'info_label'):
             self.view.info_label.config(text=stats_text)

    def _generate_map(self):
        random.seed(12345) 
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid_walls[y][x] = self.factory.create_hard_wall()
                elif random.random() < 0.35 and not ((x<3 and y<3) or (x>11 and y>9)):
                    if random.random() < 0.15:
                        self.grid_walls[y][x] = self.factory.create_durable_wall()
                    else:
                        self.grid_walls[y][x] = self.factory.create_soft_wall()

    def handle_input(self, key):
        if not self.running: return
        command = None
        if key == 'Up': command = MoveCommand(self.player, 0, -1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Down': command = MoveCommand(self.player, 0, 1, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Left': command = MoveCommand(self.player, -1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'Right': command = MoveCommand(self.player, 1, 0, self.grid_walls, GRID_WIDTH, GRID_HEIGHT)
        elif key == 'space': command = PlaceBombCommand(self)
        elif key == 'Escape': self.running = False; self.view.root.quit()

        if command:
            command.execute()
            self.check_powerups()

    def check_powerups(self):
        for p in self.powerups:
            if p.active and p.x == self.player.x and p.y == self.player.y:
                p.active = False
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

    def game_over(self, result):
        if not self.running: return
        self.running = False
        
        is_win = (result == "WIN")
        # Veritabanını güncelle
        self.repo.update_stats(self.username, is_win)
        
        msg = "KAZANDIN!" if is_win else "KAYBETTİN!"
        color = "#4CAF50" if is_win else "#F44336"
        self.view.show_game_over(msg, color)
        print(f"Oyun Bitti: {result}. İstatistik güncellendi.")

    def game_loop(self):
        if not self.running: return
        current_time = time.time() * 1000
        
        # --- 1. AĞ SENKRONİZASYONU ---
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
                
                if "killed_enemies" in reply:
                    for enemy_idx in reply["killed_enemies"]:
                        if enemy_idx < len(self.enemies) and self.enemies[enemy_idx].is_alive:
                            self.enemies[enemy_idx].is_alive = False

                # Multiplayer Kazanma Kontrolü
                if "alive" in reply and not reply["alive"] and self.player.is_alive:
                    self.game_over("WIN")
                    return
        except Exception as e:
            pass # Bağlantı yoksa devam et

        # --- 2. OYUNCU DURUMU ---
        if not self.player.is_alive:
            self.game_over("LOSE")
            return

        # --- 3. PATLAMALAR ---
        bombs_to_remove = []
        for bomb in self.bombs:
            explosion_area = bomb.check_explosion(current_time, GRID_WIDTH, GRID_HEIGHT, self.grid_walls)
            if explosion_area:
                bombs_to_remove.append(bomb)
                self.view.show_explosion(explosion_area)
                
                for (ex, ey) in explosion_area:
                    # Duvar Kırma
                    wall = self.grid_walls[ey][ex]
                    if wall and wall.is_breakable():
                        if hasattr(wall, 'take_damage'):
                            if wall.take_damage(): self.grid_walls[ey][ex] = None
                        else:
                            self.grid_walls[ey][ex] = None
                            if random.random() < 0.3: self.powerups.append(PowerUpItem(ex, ey))
                    
                    # Düşman Öldürme
                    for idx, enemy in enumerate(self.enemies):
                        if enemy.is_alive and enemy.x == ex and enemy.y == ey:
                            enemy.is_alive = False
                            self.last_killed_enemies.append(idx)
                            print("Düşman öldürüldü!")

        for b in bombs_to_remove: self.bombs.remove(b)

        # --- 4. KAZANMA KONTROLÜ (YENİ - SINGLE PLAYER İÇİN) ---
        # Eğer tüm düşmanlar öldüyse KAZAN
        active_enemies = [e for e in self.enemies if e.is_alive]
        if not active_enemies and self.player.is_alive:
             self.game_over("WIN")
             return

        # --- 5. DÜŞMAN HAREKETİ ---
        if int(time.time() * 10) % 5 == 0:
            for enemy in self.enemies:
                if enemy.is_alive:
                    enemy.move((self.player.x, self.player.y), self.grid_walls)
                    if enemy.x == self.player.x and enemy.y == self.player.y:
                        self.player.kill()

        # --- 6. ÇİZİM ---
        all_entities = self.enemies + [self.opponent]
        self.view.draw(self.grid_walls, self.player, all_entities, self.bombs, self.powerups)
        
        self.view.root.after(50, self.game_loop)