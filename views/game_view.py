import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Pillow kütüphanesi şart
import os
from config import WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE

class GameView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.root = parent 
        self.controller = None
        
        # Tüm pencereyi kapla
        self.pack(fill="both", expand=True)
        self.images = {}
        
        # --- LAYOUT AYARLARI ---
        self.main_container = tk.Frame(self, bg="#121212")
        self.main_container.pack(fill="both", expand=True)
        
        # 1. Oyun Alanı (Canvas) - Sol Taraf
        # Padx ve Pady değerlerini düşürdük ki sığsın
        self.game_frame = tk.Frame(self.main_container, bg="#333", bd=2, relief="sunken")
        self.game_frame.pack(side="left", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.game_frame, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#2d2d2d", highlightthickness=0)
        self.canvas.pack()
        
        # 2. Bilgi Paneli (Sidebar) - Sağ Taraf
        self.sidebar = tk.Frame(self.main_container, bg="#1E1E1E", width=250)
        self.sidebar.pack(side="right", fill="y", expand=True)
        self.sidebar.pack_propagate(False)

        self.create_sidebar_widgets()
        
        # Resimleri Yükle ve Boyutlandır
        self._load_images()

        # Klavye dinleme
        self.parent.bind("<KeyPress>", self.on_key_press)
        self.canvas.focus_set()

    def _load_images(self):
        """Resimleri yükler ve 40x40 piksele otomatik boyutlandırır."""
        base_folder = os.getcwd()
        assets_folder = os.path.join(base_folder, "assets")
        
        # Resim dosya isimleri
        image_files = {
            "hard": "wall_hard.png",
            "soft": "wall_soft.png",
            "player": "player.png",
            "enemy": "enemy.png",
            "bomb": "bomb.png",
            "powerup": "powerup.png"
        }

        try:
            for key, filename in image_files.items():
                path = os.path.join(assets_folder, filename)
                if os.path.exists(path):
                    # PIL ile resmi aç
                    img = Image.open(path)
                    
                    # Şeffaflık (Alpha) kanalını koru
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                        
                    # Otomatik Boyutlandırma (CELL_SIZE x CELL_SIZE)
                    # LANCZOS filtresi ile kaliteli küçültme
                    img = img.resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
                    
                    # Tkinter formatına çevirip kaydet
                    self.images[key] = ImageTk.PhotoImage(img)
                else:
                    print(f"UYARI: {filename} bulunamadı!")
            print("Resimler başarıyla yüklendi ve boyutlandırıldı.")
            
        except Exception as e:
            print(f"Resim işleme hatası: {e}")

    def bind_keys(self, handler):
        self.input_handler = handler

    def on_key_press(self, event):
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler(event.keysym)
        elif self.controller:
            self.controller.handle_input(event.keysym)

    def create_sidebar_widgets(self):
        # Başlık
        lbl_title = tk.Label(self.sidebar, text="STATS", font=("Impact", 20), bg="#1E1E1E", fg="#FF9800")
        lbl_title.pack(pady=(20, 10))
        
        # Info Label (Controller buraya yazar)
        self.info_frame = tk.Frame(self.sidebar, bg="#1E1E1E")
        self.info_frame.pack(fill="x", padx=10, pady=5)
        
        self.info_label = tk.Label(self.info_frame, text="Loading...", font=("Helvetica", 9), bg="#1E1E1E", fg="#BDBDBD", wraplength=230, justify="center")
        self.info_label.pack()

        # Skor Kutusu
        self.score_frame = tk.Frame(self.sidebar, bg="#2C2C2C", bd=1, relief="solid")
        self.score_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(self.score_frame, text="GAME SCORE", font=("Helvetica", 10, "bold"), bg="#2C2C2C", fg="#AAA").pack(pady=(5,0))
        self.score_label = tk.Label(self.score_frame, text="0", font=("Consolas", 24, "bold"), bg="#2C2C2C", fg="#4CAF50")
        self.score_label.pack(pady=(0, 10))

        # Kontroller Bilgisi
        info_text = "CONTROLS\n\nWASD/Arrow: Move\nSPACE: Bomb\nESC: Quit"
        lbl_info = tk.Label(self.sidebar, text=info_text, font=("Consolas", 10), bg="#1E1E1E", fg="#666", justify="left")
        lbl_info.pack(side="bottom", pady=20)

    def set_controller(self, controller):
        self.controller = controller

    def set_background(self, color):
        # Canvas rengini değiştirmeye gerek yok, modern tema sabit kalsın.
        # İstenirse: self.canvas.config(bg=color) yapılabilir.
        pass

    def draw(self, grid, player, enemies, bombs, powerups):
        self.canvas.delete("all")
        
        # 1. Duvarları Çiz
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                wall = grid[y][x]
                if wall:
                    img_key = "soft" if wall.is_breakable() else "hard"
                    if img_key in self.images: 
                        self.draw_image(x, y, self.images[img_key])
                    else: 
                        self.draw_cell_rect(x, y, wall.get_color())
        
        # 2. Powerups Çiz
        for p in powerups:
            if p.active:
                if "powerup" in self.images: self.draw_image(p.x, p.y, self.images["powerup"])
                else: self.draw_cell_rect(p.x, p.y, "gold", padding=10)

        # 3. Bombaları Çiz
        for b in bombs:
            if "bomb" in self.images: self.draw_image(b.x, b.y, self.images["bomb"])
            else: self.draw_circle(b.x, b.y, "red")

        # 4. Düşmanları Çiz
        for e in enemies:
            if e.is_alive:
                img_key = e.get_image_key() if hasattr(e, 'get_image_key') else 'enemy'
                if img_key in self.images: 
                    self.draw_image(e.x, e.y, self.images[img_key])
                else: 
                    self.draw_cell_rect(e.x, e.y, "blue", padding=5)

        # 5. Oyuncuyu Çiz
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
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#FF5722", outline="#FFC107", width=2)
        self.root.update()

    def show_game_over(self, message="GAME OVER", color="red"):
        self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, text=message, fill=color, font=("Impact", 40))
        messagebox.showinfo("Oyun Bitti", message)