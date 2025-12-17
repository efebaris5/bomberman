# views/login_view.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import DatabaseRepository

class LoginView:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.repo = DatabaseRepository()
        
        self.root.title("Bomberman Giriş - Design Patterns 2025")
        self.root.geometry("400x350")
        self.root.configure(bg="#2d2d2d")

        # Başlık
        tk.Label(root, text="BOMBERMAN LOGIN", font=("Arial", 20, "bold"), bg="#2d2d2d", fg="orange").pack(pady=20)

        # Kullanıcı Adı
        tk.Label(root, text="Kullanıcı Adı:", bg="#2d2d2d", fg="white").pack()
        self.entry_user = tk.Entry(root)
        self.entry_user.pack(pady=5)

        # Şifre
        tk.Label(root, text="Şifre:", bg="#2d2d2d", fg="white").pack()
        self.entry_pass = tk.Entry(root, show="*")
        self.entry_pass.pack(pady=5)

        # Tema Seçimi
        tk.Label(root, text="Tema Seç (Kayıt İçin):", bg="#2d2d2d", fg="white").pack()
        self.combo_theme = ttk.Combobox(root, values=["Forest", "City", "Desert"], state="readonly")
        self.combo_theme.current(0) # Varsayılan Forest
        self.combo_theme.pack(pady=5)

        # Butonlar
        tk.Button(root, text="GİRİŞ YAP", command=self.login, bg="green", fg="white", width=15).pack(pady=10)
        tk.Button(root, text="KAYIT OL", command=self.register, bg="blue", fg="white", width=15).pack(pady=5)
        tk.Button(root, text="SKOR TABLOSU", command=self.show_leaderboard, bg="purple", fg="white", width=15).pack(pady=5)

    def login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        selected_theme = self.combo_theme.get() # Kutudan seçilen temayı al

        # Önce bilgileri kontrol et (Eski temayla gelir)
        user_data = self.repo.login_user(user, pwd)
        
        if user_data:
            # Giriş başarılı! Şimdi seçilen temayı veritabanına kaydet
            self.repo.update_user_theme(user, selected_theme)
            
            # user_data normalde değiştirilemez bir 'tuple'dır.
            # Onu listeye çevirip 4. indeksteki (tema) veriyi güncelliyoruz.
            # user_data yapısı: [id, username, wins, losses, theme]
            user_data_list = list(user_data)
            user_data_list[4] = selected_theme 
            
            messagebox.showinfo("Başarılı", f"Hoşgeldin {user}!\nSeçilen Tema: {selected_theme}")
            
            # Güncellenmiş listeyi oyuna gönder
            self.on_login_success(user_data_list) 
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")
    def register(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        theme = self.combo_theme.get()
        if not user or not pwd:
            messagebox.showwarning("Uyarı", "Alanlar boş olamaz!")
            return
            
        if self.repo.register_user(user, pwd, theme):
            messagebox.showinfo("Başarılı", f"Kayıt oluşturuldu! Tema: {theme}")
        else:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor.")
           
    def show_leaderboard(self):
        top_players = self.repo.get_leaderboard()
        
        if not top_players:
            messagebox.showinfo("Skor Tablosu", "Henüz kayıtlı oyun verisi yok.")
            return
            
        leaderboard_text = "🏆 EN ÇOK KAZANANLAR 🏆\n\n"
        for i, (user, wins) in enumerate(top_players, 1):
            leaderboard_text += f"{i}. {user} - {wins} Galibiyet\n"
            
        messagebox.showinfo("Skor Tablosu", leaderboard_text)