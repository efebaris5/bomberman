from interfaces import Command

class MoveCommand(Command):
    # __init__ metoduna 'on_step_callback' parametresi ekledik
    def __init__(self, player, dx, dy, grid_walls, grid_width, grid_height, on_step_callback=None):
        self.player = player
        self.dx = dx
        self.dy = dy
        self.grid = grid_walls
        self.width = grid_width
        self.height = grid_height
        self.on_step_callback = on_step_callback # Kontrol fonksiyonunu sakla

    def execute(self):
        if not self.player.is_alive: return

        # Hızı al
        speed = 1
        if hasattr(self.player, "get_speed"):
             speed = self.player.get_speed()
        
        moved_at_least_once = False

        # Adım adım ilerleme döngüsü
        for _ in range(speed):
            nx = self.player.x + self.dx
            ny = self.player.y + self.dy

            # Harita sınırları ve duvar kontrolü
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[ny][nx] is None: # Duvar yoksa ilerle
                    self.player.set_pos(nx, ny)
                    moved_at_least_once = True
                    
                    # --- KRİTİK DÜZELTME ---
                    # Her adım attığımızda power-up kontrolünü çalıştır
                    if self.on_step_callback:
                        self.on_step_callback()
                else:
                    # Duvar varsa dur
                    break
            else:
                # Harita dışıysa dur
                break
        
        return moved_at_least_once

class PlaceBombCommand(Command):
    def __init__(self, game_controller):
        self.controller = game_controller

    def execute(self):
        if self.controller.player.is_alive:
            self.controller.place_bomb()