# controllers/game_controller.py
import time
import random
import json
from config import GRID_WIDTH, GRID_HEIGHT
from database import DatabaseRepository
# DesertThemeFactory EKLENDİ
from patterns.factories import ForestThemeFactory, CityThemeFactory, DesertThemeFactory
from patterns.strategies import RandomStrategy
from patterns.decorators import BombPowerUp
from models.entities import Player, Enemy, Bomb, PowerUpItem
from network import Network

class GameController:
    def __init__(self, view, user_data):
        self.view = view
        self.repo = DatabaseRepository()
        
        self.user_id = user_data[0]
        self.username = user_data[1]
        self.wins = user_data[2]
        self.losses = user_data[3]
        
        self.net = Network()
        self.player_id = self.net.player_id
        
        # --- TEMA SEÇİMİ (Artık 3 Seçenek Var) ---
        theme_choice = random.choice(["Forest", "City", "Desert"])
        if theme_choice == "Forest":
            self.factory = ForestThemeFactory()
        elif theme_choice == "City":
            self.factory = CityThemeFactory()
        else:
            self.factory = DesertThemeFactory()
            
        print(f"Seçilen Tema: {theme_choice}")
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

        self.enemies = [Enemy(7, 6, RandomStrategy())]
        self.bombs = []
        self.running = True
        
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
        if not self.player.is_alive: return
        dx, dy = 0, 0
        if key == 'Up': dy = -1
        elif key == 'Down': dy = 1
        elif key == 'Left': dx = -1
        elif key == 'Right': dx = 1
        elif key == 'space': self.place_bomb()

        nx, ny = self.player.x + dx, self.player.y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and self.grid_walls[ny][nx] is None:
            self.player.set_pos(nx, ny)
            self.check_powerups()

    def check_powerups(self):
        for p in self.powerups:
            if p.active and p.x == self.player.x and p.y == self.player.y:
                p.active = False
                self.player = BombPowerUp(self.player)
                
    def place_bomb(self):
        bomb = Bomb(self.player.x, self.player.y, self.player.get_bomb_power())
        bomb.add_observer(self.player) 
        bomb.add_observer(self.opponent)
        self.bombs.append(bomb)

    def game_over(self, result):
        if not self.running: return
        self.running = False
        is_win = (result == "WIN")
        self.repo.update_stats(self.username, is_win)
        msg = "KAZANDIN!" if is_win else "KAYBETTİN!"
        color = "green" if is_win else "red"
        self.view.show_game_over(msg, color)

    def game_loop(self):
        if not self.running: return
        current_time = time.time() * 1000
        
        try:
            my_data = {"x": self.player.x, "y": self.player.y, "alive": self.player.is_alive}
            reply = self.net.send(my_data)
            if reply:
                self.opponent.set_pos(reply["x"], reply["y"])
                if "alive" in reply and not reply["alive"] and self.player.is_alive:
                    self.game_over("WIN")
                    return
        except: pass

        bombs_to_remove = []
        for bomb in self.bombs:
            explosion_area = bomb.check_explosion(current_time, GRID_WIDTH, GRID_HEIGHT, self.grid_walls)
            if explosion_area:
                bombs_to_remove.append(bomb)
                self.view.show_explosion(explosion_area)
                
                for (ex, ey) in explosion_area:
                    wall = self.grid_walls[ey][ex]
                    
                    if wall and wall.is_breakable():
                        # --- SERT DUVAR MANTIĞI ---
                        # Eğer duvarın 'take_damage' özelliği varsa (Sert Duvar ise)
                        if hasattr(wall, 'take_damage'):
                            destroyed = wall.take_damage() # Canını azalt
                            if destroyed:
                                self.grid_walls[ey][ex] = None
                                self.repo.save_score(self.repo.get_highscore() + 20)
                        else:
                            # Normal duvar ise direkt yok et
                            self.grid_walls[ey][ex] = None
                            self.repo.save_score(self.repo.get_highscore() + 10)
                            if random.random() < 0.3:
                                self.powerups.append(PowerUpItem(ex, ey))
                        # -------------------------
                        
        for b in bombs_to_remove: self.bombs.remove(b)

        if int(time.time() * 10) % 5 == 0:
            for enemy in self.enemies:
                enemy.move((self.player.x, self.player.y), self.grid_walls)
                if enemy.x == self.player.x and enemy.y == self.player.y and enemy.is_alive:
                    self.player.kill()

        all_entities = self.enemies + [self.opponent]
        self.view.draw(self.grid_walls, self.player, all_entities, self.bombs, self.powerups)
        
        if self.player.is_alive:
            self.view.root.after(50, self.game_loop)
        else:
            self.game_over("LOSE")