# views/login_view.py
import tkinter as tk
from tkinter import messagebox
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

        # Butonlar
        tk.Button(root, text="GİRİŞ YAP", command=self.login, bg="green", fg="white", width=15).pack(pady=10)
        tk.Button(root, text="KAYIT OL", command=self.register, bg="blue", fg="white", width=15).pack(pady=5)

    def login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        user_data = self.repo.login_user(user, pwd)
        
        if user_data:
            messagebox.showinfo("Başarılı", f"Hoşgeldin {user}!\nKazanma: {user_data[2]} | Kaybetme: {user_data[3]}")
            self.on_login_success(user_data) # Ana oyuna geçiş yap
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")

    def register(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        if not user or not pwd:
            messagebox.showwarning("Uyarı", "Alanlar boş olamaz!")
            return
            
        if self.repo.register_user(user, pwd):
            messagebox.showinfo("Başarılı", "Kayıt oluşturuldu! Şimdi giriş yapabilirsiniz.")
        else:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten kullanılıyor.")