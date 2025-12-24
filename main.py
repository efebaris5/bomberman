import tkinter as tk
from tkinter import messagebox
from views.login_view import LoginView
from views.game_view import GameView
from controllers.game_controller import GameController
from database import DatabaseRepository

class MainApp:
    def __init__(self):
        self.repo = DatabaseRepository()
        self.root = tk.Tk()
        self.root.title("Bomberman 2025")
        self.root.geometry("1280x800")
        
        self.current_view = None
        self.game_controller = None
        
        self.show_login()
        
    def show_login(self):
        # Eğer açık bir controller varsa durdur
        if self.game_controller:
            self.game_controller.running = False

        if self.current_view: 
            self.current_view.destroy()
            
        self.current_view = LoginView(self.root)
        self.current_view.set_controller(self)
        self.current_view.pack(fill="both", expand=True)
        
    def show_game(self, user_data):
        if self.current_view: 
            self.current_view.destroy()
        
        # Oyun ekranını oluştur
        self.current_view = GameView(self.root)
        self.current_view.pack(fill="both", expand=True)
        
        # GameController başlat
        self.game_controller = GameController(self.current_view, user_data)
        
        # --- İŞTE EKSİK OLAN SATIR BU ---
        # Görüntüye (View) kontrolcüsünü (Controller) tanıtıyoruz
        self.current_view.set_controller(self.game_controller)
        # --------------------------------
        
        # GameController'a "Menüye Dön" denildiğinde show_login'i çalıştır diyoruz
        self.game_controller.on_exit_callback = self.show_login 
        
    def login(self, username, password, theme):
        """Kullanıcı giriş işlemi."""
        user = self.repo.login_user(username, password)
        if user:
            if theme:
                self.repo.update_user_theme(username, theme)
                user = self.repo.login_user(username, password)
            
            self.show_game(user)
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

    def register(self, username, password, theme):
        """Yeni kullanıcı kayıt işlemi."""
        if self.repo.register_user(username, password, theme):
            return True, "Kayıt Başarılı! Şimdi giriş yapabilirsiniz."
        return False, "Bu kullanıcı adı zaten alınmış."
        
    def get_leaderboard_data(self):
        return self.repo.get_leaderboard()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()