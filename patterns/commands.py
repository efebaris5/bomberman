from interfaces import Command

class MoveCommand(Command):
    def __init__(self, player, dx, dy, grid_walls, grid_width, grid_height):
        self.player = player
        self.dx = dx
        self.dy = dy
        self.grid = grid_walls
        self.width = grid_width
        self.height = grid_height

    def execute(self):
        if not self.player.is_alive: return

        # Hızı al
        speed = 1
        if hasattr(self.player, "get_speed"):
             speed = self.player.get_speed()
        
        # dx ve dy'yi hızla çarp
        step_x = self.dx * speed
        step_y = self.dy * speed

        nx = self.player.x + step_x
        ny = self.player.y + step_y
        # Harita sınırları ve duvar kontrolü
        if 0 <= nx < self.width and 0 <= ny < self.height:
            if self.grid[ny][nx] is None: # Duvar yoksa ilerle
                self.player.set_pos(nx, ny)
                return True # Hareket başarılı
        return False

class PlaceBombCommand(Command):
    def __init__(self, game_controller):
        self.controller = game_controller

    def execute(self):
        if self.controller.player.is_alive:
            self.controller.place_bomb()