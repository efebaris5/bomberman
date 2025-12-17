# patterns/strategies.py
import random
import heapq
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
    # --- BONUS: A* (A-Star) Akıllı Yol Bulma ---
class AStarStrategy(MoveStrategy):
    def move(self, enemy_pos, player_pos, grid):
        start = enemy_pos
        goal = player_pos
        
        # Eğer zaten hedeftelerse kıpırdama
        if start == goal:
            return start

        # A* Algoritması Hazırlığı
        # Priority Queue: (f_score, x, y) şeklinde tutar
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        
        # g_score: Başlangıçtan buraya gelmenin maliyeti
        g_score = {start: 0}
        
        # f_score: g_score + heuristic (tahmini kalan yol)
        f_score = {start: self.heuristic(start, goal)}
        
        path_found = False
        
        while open_set:
            # En düşük maliyetli kareyi seç
            current = heapq.heappop(open_set)[1]
            
            # Hedefe ulaştık mı?
            if current == goal:
                path_found = True
                break
            
            # Komşulara bak (Sağ, Sol, Aşağı, Yukarı)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # Harita sınırları içinde mi?
                if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
                    # Duvar var mı? (Oyuncu bir duvarın üzerindeyse oraya da gitmeli, o yüzden neighbor == goal kontrolü var)
                    if grid[neighbor[1]][neighbor[0]] is None or neighbor == goal:
                        tentative_g_score = g_score[current] + 1
                        
                        # Daha iyi bir yol bulduysak kaydet
                        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f = tentative_g_score + self.heuristic(neighbor, goal)
                            heapq.heappush(open_set, (f, neighbor))
        
        if path_found:
            return self.reconstruct_path(came_from, current, start)
        
        # Yol bulamazsa olduğu yerde beklesin (veya rastgele hareket etsin)
        return start

    def heuristic(self, a, b):
        # Manhattan Mesafesi: |x1 - x2| + |y1 - y2|
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current, start):
        # Yolu geriye doğru takip et
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        
        # Yol listesini ters çevir (Başlangıç -> Hedef)
        path.reverse()
        
        # İlk adımı döndür (Şu anki konumdan sonraki ilk kare)
        if len(path) > 0:
            return path[0]
        return start