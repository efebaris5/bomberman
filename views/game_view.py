# views/game_view.py
import tkinter as tk
import os
from config import WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE

class GameView:
    def __init__(self, root):
        self.root = root
        self.root.title("Bomberman - Design Patterns 2025")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#2d2d2d")
        self.canvas.pack()
        self.info_label = tk.Label(root, text="Score: 0", font=("Arial", 14))
        self.info_label.pack()
        self.images = {}
        self._load_images()

    def _load_images(self):
        # Dosya yolu düzeltmesi: main.py'nin olduğu yerden assets'e git
        base_folder = os.getcwd() 
        assets_folder = os.path.join(base_folder, "assets")
        try:
            self.images["hard"] = tk.PhotoImage(file=os.path.join(assets_folder, "wall_hard.png"))
            self.images["soft"] = tk.PhotoImage(file=os.path.join(assets_folder, "wall_soft.png"))
            self.images["player"] = tk.PhotoImage(file=os.path.join(assets_folder, "player.png"))
            self.images["enemy"] = tk.PhotoImage(file=os.path.join(assets_folder, "enemy.png"))
            self.images["bomb"] = tk.PhotoImage(file=os.path.join(assets_folder, "bomb.png"))
            self.images["powerup"] = tk.PhotoImage(file=os.path.join(assets_folder, "powerup.png"))
            print("Resimler yüklendi.")
        except Exception as e:
            print(f"Resimler bulunamadı, renkli kutular kullanılacak. Hata: {e}")

    def bind_keys(self, handler):
        self.root.bind("<Up>", lambda e: handler('Up'))
        self.root.bind("<Down>", lambda e: handler('Down'))
        self.root.bind("<Left>", lambda e: handler('Left'))
        self.root.bind("<Right>", lambda e: handler('Right'))
        self.root.bind("<space>", lambda e: handler('space'))

    def draw(self, grid, player, enemies, bombs, powerups):
        self.canvas.delete("all")
        # Grid
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                wall = grid[y][x]
                if wall:
                    img_key = "soft" if wall.is_breakable() else "hard"
                    if img_key in self.images: self.draw_image(x, y, self.images[img_key])
                    else: self.draw_cell_rect(x, y, wall.get_color())
        
        # Powerups
        for p in powerups:
            if p.active:
                if "powerup" in self.images: self.draw_image(p.x, p.y, self.images["powerup"])
                else: self.draw_cell_rect(p.x, p.y, "gold", padding=10)

        # Bombs
        for b in bombs:
            if "bomb" in self.images: self.draw_image(b.x, b.y, self.images["bomb"])
            else: self.draw_circle(b.x, b.y, "red")

        # Enemies
        for e in enemies:
            if e.is_alive:
                # Eskiden burada sadece "enemy" yazıyordu.
                # Şimdi dinamik olarak nesneden istiyoruz.
                img_key = e.get_image_key() 
                
                if img_key in self.images: 
                    self.draw_image(e.x, e.y, self.images[img_key])
                else: 
                    self.draw_cell_rect(e.x, e.y, "blue", padding=5)

        # Player
        if player.is_alive:
            if "player" in self.images: self.draw_image(player.x, player.y, self.images["player"])
            else: self.draw_cell_rect(player.x, player.y, "white", padding=8)

    def draw_image(self, x, y, image):
        cx, cy = x * CELL_SIZE + (CELL_SIZE / 2), y * CELL_SIZE + (CELL_SIZE / 2)
        self.canvas.create_image(cx, cy, image=image)

    def draw_cell_rect(self, x, y, color, padding=1):
        x1, y1 = x * CELL_SIZE + padding, y * CELL_SIZE + padding
        x2, y2 = (x + 1) * CELL_SIZE - padding, (y + 1) * CELL_SIZE - padding
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    def draw_circle(self, x, y, color):
        p = 5
        self.canvas.create_oval(x*CELL_SIZE+p, y*CELL_SIZE+p, (x+1)*CELL_SIZE-p, (y+1)*CELL_SIZE-p, fill=color)

    def show_explosion(self, coords):
        for (x, y) in coords:
            x1, y1 = x * CELL_SIZE, y * CELL_SIZE
            x2, y2 = (x+1) * CELL_SIZE, (y+1) * CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="orange", outline="")
        self.root.update()

    def show_game_over(self, message="GAME OVER", color="red"):
        self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, text=message, fill=color, font=("Arial", 40, "bold"))
    
    def set_background(self, color):
        self.canvas.configure(bg=color)