# main.py
import tkinter as tk
from views.login_view import LoginView
from views.game_view import GameView
from controllers.game_controller import GameController

def start_game(user_data):
    # Giriş ekranını kapat
    for widget in root.winfo_children():
        widget.destroy()
        
    # Oyun ekranını başlat
    view = GameView(root)
    # Controller'a kullanıcı verisini de gönderiyoruz
    controller = GameController(view, user_data)

if __name__ == "__main__":
    root = tk.Tk()
    # İlk açılışta Login View çalışacak
    app = LoginView(root, start_game)
    root.mainloop()