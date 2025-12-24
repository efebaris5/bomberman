import time
from interfaces import GameObject, Observer, Subject, IPlayer, MoveStrategy

class Player(GameObject, Observer, IPlayer):
    def __init__(self, x, y):
        super().__init__(x, y)
        self._is_alive = True
        self.health = 1  
        self._bomb_power = 1
        self._max_bombs = 1
        self._speed = 1 

    def get_speed(self): return self._speed
    
    def get_bomb_power(self): return self._bomb_power
    def get_max_bombs(self): return self._max_bombs
    def get_image_key(self): return "player"
    
    def kill(self):
        """Oyuncuyu doğrudan öldürür."""
        self._is_alive = False
        self.health = 0
        print("Oyuncu öldü!")

    # --- EKLENDİ: Testlerin beklediği hasar alma fonksiyonu ---
    def take_damage(self):
        """Canı 1 azaltır, 0 olursa öldürür."""
        if not self._is_alive: return
        
        self.health -= 1
        print(f"Oyuncu hasar aldı! Kalan Can: {self.health}")
        
        if self.health <= 0:
            self.kill()

    @property
    def is_alive(self): return self._is_alive
    
    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def update(self, event_type, data):
        """Observer metodu: Patlama olunca tetiklenir."""
        if event_type == "EXPLOSION":
            if (self.x, self.y) in data:
                # --- GÜNCELLENDİ: Direkt kill() yerine hasar alıyor ---
                self.take_damage() 

class Enemy(GameObject, Observer):
    def __init__(self, x, y, strategy: MoveStrategy):
        super().__init__(x, y)
        self.strategy = strategy
        self.is_alive = True
    
    def get_image_key(self): 
        return "enemy"
    
    def move(self, player_pos, grid):
        if self.is_alive:
            self.x, self.y = self.strategy.move((self.x, self.y), player_pos, grid)
    
    def update(self, event_type, data):
        if event_type == "EXPLOSION":
            if (self.x, self.y) in data:
                self.is_alive = False
                print("Düşman yok edildi!")

class PowerUpItem(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.active = True

class Bomb(Subject):
    def __init__(self, x, y, power=1):
        super().__init__()
        self.x = x
        self.y = y
        self.power = power
        self.timer = 2000 
        self.start_time = time.time() * 1000
        self.exploded = False

    def check_explosion(self, current_time, grid_width, grid_height, grid_walls):
        if not self.exploded and (current_time - self.start_time) > self.timer:
            self.exploded = True
            affected_cells = [(self.x, self.y)]
            directions = [(0,1), (0,-1), (1,0), (-1,0)]
            for dx, dy in directions:
                for i in range(1, self.power + 1):
                    nx, ny = self.x + (dx*i), self.y + (dy*i)
                    if 0 <= nx < grid_width and 0 <= ny < grid_height:
                        wall = grid_walls[ny][nx]
                        if wall:
                            if wall.is_breakable():
                                affected_cells.append((nx, ny))
                            break 
                        affected_cells.append((nx, ny))
            self.notify("EXPLOSION", affected_cells)
            return affected_cells
        return None