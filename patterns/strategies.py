# patterns/strategies.py
import random
from config import GRID_WIDTH, GRID_HEIGHT
from interfaces import MoveStrategy

class RandomStrategy(MoveStrategy):
    def move(self, enemy_pos, player_pos, grid):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x, new_y = enemy_pos[0] + dx, enemy_pos[1] + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and grid[new_y][new_x] is None:
            return (new_x, new_y)
        return enemy_pos

class ChasingStrategy(MoveStrategy):
    def move(self, enemy_pos, player_pos, grid):
        ex, ey = enemy_pos
        px, py = player_pos
        best_move = enemy_pos
        min_dist = float('inf')
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] is None:
                dist = abs(nx - px) + abs(ny - py)
                if dist < min_dist:
                    min_dist = dist
                    best_move = (nx, ny)
        return best_move