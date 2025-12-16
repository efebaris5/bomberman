# database.py
import sqlite3
import hashlib

class DatabaseRepository:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseRepository, cls).__new__(cls)
            cls._instance.init_db()
        return cls._instance

    def init_db(self):
        self.conn = sqlite3.connect("bomberman_game.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Kullanıcılar Tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0
            )
        ''')
        
        # Skorlar Tablosu (High Score için)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        """Yeni kullanıcı kaydeder. Başarılıysa True döner."""
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, pwd_hash))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Bu kullanıcı adı zaten var

    def login_user(self, username, password):
        """Giriş başarılıysa kullanıcı verilerini döner, değilse None."""
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT id, username, wins, losses FROM users WHERE username=? AND password=?", (username, pwd_hash))
        return self.cursor.fetchone()

    def update_stats(self, username, is_win):
        """Maç sonucuna göre istatistikleri günceller."""
        if is_win:
            self.cursor.execute("UPDATE users SET wins = wins + 1 WHERE username = ?", (username,))
        else:
            self.cursor.execute("UPDATE users SET losses = losses + 1 WHERE username = ?", (username,))
        self.conn.commit()
        print(f"[DB] {username} için istatistik güncellendi (Kazanma: {is_win})")

    def save_score(self, score):
        try:
            current_high = self.get_highscore()
            if score > current_high:
                self.cursor.execute("INSERT INTO scores (score) VALUES (?)", (score,))
                self.conn.commit()
        except Exception as e:
            print(f"[DB Hata]: {e}")

    def get_highscore(self):
        try:
            self.cursor.execute("SELECT MAX(score) FROM scores")
            result = self.cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except:
            return 0