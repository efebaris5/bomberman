import tkinter as tk
from PIL import Image, ImageTk
import os
from config import GRID_WIDTH, GRID_HEIGHT

class GameView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)
        self.controller = None
        
        # --- DİNAMİK BOYUTLAR ---
        self.cell_w = 40 # Varsayılan
        self.cell_h = 40
        self.images = {} # Resim önbelleği
        
        # Canvas
        self.canvas = tk.Canvas(self, bg="#355E3B")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Sağ Panel (Sidebar)
        self.sidebar = tk.Frame(self, width=200, bg="#2d2d2d")
        self.sidebar.pack(side="right", fill="y")
        
        # Sidebar İçeriği
        self.logo_lbl = tk.Label(self.sidebar, text="BOMBERMAN", font=("Impact", 20), bg="#2d2d2d", fg="#FF9800")
        self.logo_lbl.pack(pady=20)
        
        self.info_label = tk.Label(self.sidebar, text="Loading...", font=("Consolas", 12), bg="#2d2d2d", fg="white", justify="left")
        self.info_label.pack(pady=10, padx=10)
        
        controls = "CONTROLS:\nArrow Keys: Move\nSpace: Bomb\nESC: Quit"
        tk.Label(self.sidebar, text=controls, font=("Helvetica", 10), bg="#2d2d2d", fg="#aaa", justify="left").pack(side="bottom", pady=20)

        # --- KRİTİK: Pencere Boyutu Değişince Çalışır ---
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.canvas.focus_set()

    def set_controller(self, controller):
        self.controller = controller

    def on_resize(self, event):
        """Pencere boyutu değiştiğinde kareleri ve resimleri yeniden hesapla."""
        new_w = event.width
        new_h = event.height
        
        # Yeni hücre boyutlarını hesapla
        self.cell_w = new_w // GRID_WIDTH
        self.cell_h = new_h // GRID_HEIGHT
        
        # Resimleri bu yeni boyuta göre tekrar yükle/boyutlandır
        self.reload_images()

    def reload_images(self):
        """Resimleri güncel hücre boyutuna göre yeniden yükler."""
        assets_path = os.path.join(os.getcwd(), "assets")
        image_files = {
            "player": "player.png", "enemy": "enemy.png", "bomb": "bomb.png",
            "wall_hard": "wall_hard.png", "wall_soft": "wall_soft.png", "powerup": "powerup.png",
            "wall_durable": "wall_durable.png",
            "explosion": "explosion.png"
        }

        for key, filename in image_files.items():
            path = os.path.join(assets_path, filename)
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    # Dinamik boyutlandırma (LANCZOS kalitesiyle)
                    # En az 1 piksel olsun ki hata vermesin
                    w = max(1, self.cell_w)
                    h = max(1, self.cell_h)
                    pil_img = pil_img.resize((w, h), Image.Resampling.LANCZOS)
                    self.images[key] = ImageTk.PhotoImage(pil_img)
                except Exception as e:
                    print(f"Resim hatası ({key}): {e}")

    def bind_keys(self, callback):
        self.parent.bind("<Key>", lambda event: callback(event.keysym))

    def set_background(self, color):
        self.canvas.config(bg=color)

    # Fonksiyon artık 'explosions' parametresini de alıyor
    def draw(self, grid, player, enemies, bombs, powerups, explosions):
        self.canvas.delete("all")
        
        cw = self.cell_w
        ch = self.cell_h
        
        # 1. Duvarlar
        for r in range(GRID_HEIGHT):
            for c in range(GRID_WIDTH):
                wall = grid[r][c]
                x, y = c * cw, r * ch
                if wall:
                    img_key = wall.get_image_key() if hasattr(wall, "get_image_key") else "wall_hard"
                    if img_key in self.images:
                        self.canvas.create_image(x, y, image=self.images[img_key], anchor="nw")
                    else:
                        self.canvas.create_rectangle(x, y, x+cw, y+ch, fill=wall.get_color())

        # 2. Powerups
        for p in powerups:
            if p.active:
                x, y = p.x * cw, p.y * ch
                if "powerup" in self.images:
                    self.canvas.create_image(x, y, image=self.images["powerup"], anchor="nw")
                else:
                    self.canvas.create_oval(x, y, x+cw, y+ch, fill="yellow")

        # 3. Bombalar
        for bomb in bombs:
            x, y = bomb.x * cw, bomb.y * ch
            if "bomb" in self.images:
                self.canvas.create_image(x, y, image=self.images["bomb"], anchor="nw")
            else:
                self.canvas.create_oval(x, y, x+cw, y+ch, fill="black")

        # 4. --- YENİ: Patlamaları Çiz ---
        # Eğer 'explosion.png' varsa onu kullanır, yoksa turuncu kare çizer
        for exp in explosions:
            for (ex, ey) in exp["area"]:
                x, y = ex * cw, ey * ch
                
                # Eğer explosion resmin varsa buraya ekleyebilirsin: "explosion"
                if "explosion" in self.images:
                     self.canvas.create_image(x, y, image=self.images["explosion"], anchor="nw")
                else:
                    # Resim yoksa Klasik Turuncu Efekt
                    self.canvas.create_rectangle(x, y, x+cw, y+ch, fill="#FF4500", outline="yellow")
                    # Biraz estetik katalım (İç içe kareler)
                    self.canvas.create_rectangle(x+5, y+5, x+cw-5, y+ch-5, fill="yellow", outline="")

        # 5. Düşmanlar
        for enemy in enemies:
            if enemy.is_alive:
                x, y = enemy.x * cw, enemy.y * ch
                if "enemy" in self.images:
                    self.canvas.create_image(x, y, image=self.images["enemy"], anchor="nw")
                else:
                    self.canvas.create_oval(x, y, x+cw, y+ch, fill="red")

        # 6. Oyuncu
        if player.is_alive:
            x, y = player.x * cw, player.y * ch
            if "player" in self.images:
                self.canvas.create_image(x, y, image=self.images["player"], anchor="nw")
            else:
                self.canvas.create_oval(x, y, x+cw, y+ch, fill="blue")

    def show_explosion(self, area):
        cw, ch = self.cell_w, self.cell_h
        for (ex, ey) in area:
            self.canvas.create_rectangle(ex*cw, ey*ch, (ex+1)*cw, (ey+1)*ch, fill="orange", outline="red")

    def show_game_over(self, message, color):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        self.canvas.create_rectangle(0, 0, w, h, fill="black", stipple="gray75")
        self.canvas.create_rectangle(cx-200, cy-150, cx+200, cy+150, fill="#212121", outline="white", width=3)
        self.canvas.create_text(cx, cy-80, text=message, fill=color, font=("Impact", 40))
        
        btn_frame = tk.Frame(self.canvas, bg="#212121")
        self.canvas.create_window(cx, cy+50, window=btn_frame)
        
        tk.Button(btn_frame, text="TEKRAR OYNA", bg="#4CAF50", fg="white", width=15, command=self.restart_game).pack(pady=5)
        tk.Button(btn_frame, text="ANA MENÜ", bg="#FF9800", fg="white", width=15, command=self.return_to_menu).pack(pady=5)
        tk.Button(btn_frame, text="ÇIKIŞ", bg="#F44336", fg="white", width=15, command=self.quit_game).pack(pady=5)

    def restart_game(self):
        # Basitçe ana menüye dönüp tekrar başlatmasını sağlıyoruz
        self.return_to_menu()

    def return_to_menu(self):
        if self.controller and hasattr(self.controller, 'on_game_over_menu'):
            self.controller.on_game_over_menu()
        else:
            print("HATA: Controller bağlantısı yok!")

    def quit_game(self):
        self.parent.quit()