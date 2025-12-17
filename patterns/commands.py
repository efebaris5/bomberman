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

        # Hedef koordinatı hesapla
        nx = self.player.x + self.dx
        ny = self.player.y + self.dy

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