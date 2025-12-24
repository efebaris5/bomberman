import tkinter as tk
from tkinter import messagebox
from views.login_view import LoginView
from views.game_view import GameView
from controllers.game_controller import GameController
from database import DatabaseRepository
import config

# --- KÖPRÜ SINIFI (Bridge) ---
# --- KÖPRÜ SINIFI (Bridge) ---
class MainMenuController:
    def __init__(self, start_game_callback):
        self.start_game_callback = start_game_callback
        self.repo = DatabaseRepository() 

    # GÜNCELLEME: Artık 'theme' parametresi de alıyor
    def login(self, username, password, theme):
        user_data = self.repo.login_user(username, password)
        
        if user_data:
            # user_data yapısı: (id, username, wins, losses, db_theme)
            db_theme = user_data[4]
            
            # Eğer kutudan seçilen tema, veritabanındakinden farklıysa GÜNCELLE
            if theme and theme != db_theme:
                self.repo.update_user_theme(username, theme)
                print(f"Tema '{db_theme}' yerine '{theme}' olarak güncellendi.")
                # Oyunu yeni tema ile başlatmak için user_data'yı yeniliyoruz
                user_data = (user_data[0], user_data[1], user_data[2], user_data[3], theme)
            
            print(f"Giriş Başarılı: {username}")
            self.start_game_callback(user_data)
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")

    def register(self, username, password, theme):
        if not username or not password:
            return False, "Kullanıcı adı ve şifre boş olamaz!"
        try:
            success = self.repo.register_user(username, password, theme)
            if success:
                return True, "Kayıt başarılı! Şimdi giriş yapabilirsin."
            else:
                return False, "Bu kullanıcı adı zaten alınmış."
        except Exception as e:
            return False, f"Kayıt hatası: {e}"

    def get_leaderboard_data(self):
        return self.repo.get_leaderboard(limit=5)
# --- OYUN BAŞLATMA MANTIĞI ---
def start_game(user_data):
    # 1. Login ekranını temizle
    for widget in root.winfo_children():
        widget.destroy()

    # 2. Oyun ekranını oluştur
    game_view = GameView(root)
    game_view.pack(fill="both", expand=True)

    # 3. GameController'ı başlat
    try:
        game_controller = GameController(game_view, user_data)
        game_view.set_controller(game_controller)
        
        if hasattr(game_controller, 'start_game'):
             game_controller.start_game()
             
    except Exception as e:
        print(f"Oyun başlatılırken hata: {e}")
        messagebox.showerror("Kritik Hata", f"Oyun başlatılamadı:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bomberman 2025")
    
    window_w = config.WINDOW_WIDTH + 300 
    window_h = config.WINDOW_HEIGHT
    root.geometry(f"{window_w}x{window_h}")
    
    menu_controller = MainMenuController(start_game)
    
    app = LoginView(root)
    app.set_controller(menu_controller)
    
    root.mainloop()