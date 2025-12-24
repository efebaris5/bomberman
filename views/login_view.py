import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class LoginView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)
        self.controller = None
        self.original_bg_image = None # Orjinal resmi hafızada tutacağız
        
        # --- STİL AYARLARI ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("Game.TButton", font=("Helvetica", 10, "bold"), background="#FF9800", foreground="white", borderwidth=0)
        self.style.map("Game.TButton", background=[("active", "#F57C00")])
        
        self.style.configure("Register.TButton", font=("Helvetica", 10, "bold"), background="#4CAF50", foreground="white", borderwidth=0)
        self.style.map("Register.TButton", background=[("active", "#388E3C")])

        # --- ARKA PLAN CANVAS ---
        self.canvas = tk.Canvas(self, bg="#212121", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Resmi yükle (Ama henüz çizme, boyutlanınca çizeceğiz)
        self.load_background()

        # PENCERE BOYUTU DEĞİŞTİĞİNDE TETİKLENİR
        # Bu satır sayesinde pencere ne kadar olursa resim de o kadar olur
        self.canvas.bind('<Configure>', self._on_resize)

        # --- ANA KART (LOGIN KUTUSU) ---
        self.main_frame = tk.Frame(self, bg="#212121", bd=2, relief="ridge")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=480)

        # --- SOL PANEL (Leaderboard) ---
        self.left_frame = tk.Frame(self.main_frame, bg="#1E1E1E", width=300)
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(self.left_frame, text="TOP PLAYERS", font=("Impact", 18), bg="#1E1E1E", fg="#FFD700").pack(pady=(30, 10))
        
        self.leaderboard_container = tk.Frame(self.left_frame, bg="#1E1E1E")
        self.leaderboard_container.pack(fill="both", expand=True, padx=20)
        
        self.loading_lbl = tk.Label(self.leaderboard_container, text="Loading...", bg="#1E1E1E", fg="#666")
        self.loading_lbl.pack()

        # --- SAĞ PANEL (Form) ---
        self.right_frame = tk.Frame(self.main_frame, bg="#2d2d2d", width=400)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.create_login_widgets()

    def load_background(self):
        """Resmi diskten okur ama hemen ekrana basmaz."""
        try:
            base_path = os.getcwd()
            image_path = os.path.join(base_path, "assets", "menu_background.jpg")
            if os.path.exists(image_path):
                # Resmi PIL formatında açıp hafızada saklıyoruz
                self.original_bg_image = Image.open(image_path)
            else:
                print(f"Uyarı: {image_path} bulunamadı.")
        except Exception as e:
            print(f"Resim yükleme hatası: {e}")

    def _on_resize(self, event):
        """Pencere boyutu her değiştiğinde çalışır ve resmi yeniden boyutlandırır."""
        if not self.original_bg_image:
            return
            
        # Yeni genişlik ve yükseklik
        new_width = event.width
        new_height = event.height
        
        # Resmi yeni boyutlara göre uzat (LANCZOS kalitesiyle)
        resized_image = self.original_bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        
        # Canvas üzerindeki eski resmi sil ve yenisini koy
        self.canvas.delete("bg_img")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg_img")
        
        # Login kutusunu her zaman en üstte tut
        self.main_frame.lift()

    def create_login_widgets(self):
        # Başlık
        tk.Label(self.right_frame, text="BOMBERMAN", font=("Press Start 2P", 20, "bold"), bg="#2d2d2d", fg="#FF9800").pack(pady=(30, 5))
        tk.Label(self.right_frame, text="Login or Register", font=("Helvetica", 10), bg="#2d2d2d", fg="#AAA").pack(pady=(0, 20))

        # Kullanıcı Adı
        tk.Label(self.right_frame, text="Username", bg="#2d2d2d", fg="white", font=("Helvetica", 10)).pack(anchor="w", padx=40)
        self.entry_username = tk.Entry(self.right_frame, font=("Helvetica", 11), bg="#424242", fg="white", bd=0, insertbackground="white")
        self.entry_username.pack(fill="x", padx=40, pady=5, ipady=3)

        # Şifre
        tk.Label(self.right_frame, text="Password", bg="#2d2d2d", fg="white", font=("Helvetica", 10)).pack(anchor="w", padx=40, pady=(10, 0))
        self.entry_password = tk.Entry(self.right_frame, show="*", font=("Helvetica", 11), bg="#424242", fg="white", bd=0, insertbackground="white")
        self.entry_password.pack(fill="x", padx=40, pady=5, ipady=3)

        # Tema Seçimi
        tk.Label(self.right_frame, text="Preferred Theme", bg="#2d2d2d", fg="#BDBDBD", font=("Helvetica", 9)).pack(anchor="w", padx=40, pady=(10, 0))
        
        self.theme_var = tk.StringVar(value="Forest")
        self.combo_theme = ttk.Combobox(self.right_frame, textvariable=self.theme_var, 
                                        values=["Forest", "City", "Desert"], 
                                        state="readonly", font=("Helvetica", 10))
        self.combo_theme.pack(fill="x", padx=40, pady=5, ipady=3)

        # Butonlar
        btn_frame = tk.Frame(self.right_frame, bg="#2d2d2d")
        btn_frame.pack(fill="x", padx=40, pady=25)

        btn_login = ttk.Button(btn_frame, text="LOGIN", style="Game.TButton", command=self.handle_login)
        btn_login.pack(fill="x", pady=5)

        btn_register = ttk.Button(btn_frame, text="REGISTER", style="Register.TButton", command=self.handle_register)
        btn_register.pack(fill="x", pady=5)

    def set_controller(self, controller):
        self.controller = controller
        self.refresh_leaderboard()

    def refresh_leaderboard(self):
        for widget in self.leaderboard_container.winfo_children():
            widget.destroy()

        if self.controller:
            try:
                data = self.controller.get_leaderboard_data()
                
                # Başlık
                header = tk.Frame(self.leaderboard_container, bg="#1E1E1E")
                header.pack(fill="x", pady=(0, 5))
                tk.Label(header, text="NAME", bg="#1E1E1E", fg="#888", width=15, anchor="w").pack(side="left")
                tk.Label(header, text="WINS", bg="#1E1E1E", fg="#888", width=5, anchor="e").pack(side="right")
                
                if not data:
                    tk.Label(self.leaderboard_container, text="No records yet.", bg="#1E1E1E", fg="#666").pack(pady=20)
                
                for idx, (username, wins) in enumerate(data):
                    color = "#FFD700" if idx == 0 else "white"
                    row = tk.Frame(self.leaderboard_container, bg="#1E1E1E")
                    row.pack(fill="x", pady=2)
                    tk.Label(row, text=f"{idx+1}. {username}", bg="#1E1E1E", fg=color, width=15, anchor="w", font=("Helvetica", 10, "bold")).pack(side="left")
                    tk.Label(row, text=str(wins), bg="#1E1E1E", fg="#4CAF50", width=5, anchor="e", font=("Consolas", 10, "bold")).pack(side="right")
                    
            except Exception as e:
                print(f"Leaderboard Hatası: {e}")

    def handle_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        theme = self.theme_var.get()
        if self.controller:
            self.controller.login(username, password, theme)

    def handle_register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        theme = self.theme_var.get()
        if self.controller:
            success, message = self.controller.register(username, password, theme)
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_leaderboard()
            else:
                messagebox.showerror("Error", message)