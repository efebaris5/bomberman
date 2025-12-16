# models/walls.py
from interfaces import Wall

# 1. KIRILMAZ DUVAR (Çerçeve ve Sabitler)
class StoneWall(Wall):
    def get_color(self): return "#444444" # Koyu Gri
    def is_breakable(self): return False

# 2. KIRILABİLİR DUVARLAR (Tek Vuruş)
class BrickWall(Wall):
    def get_color(self): return "#A0522D" # Tuğla Rengi
    def is_breakable(self): return True

class TreeWall(Wall):
    def get_color(self): return "#228B22" # Orman Yeşili
    def is_breakable(self): return True

class SandWall(Wall): # (YENİ - Çöl İçin)
    def get_color(self): return "#EDC9AF" # Kum Rengi
    def is_breakable(self): return True

# 3. SERT DUVAR (YENİ - 2 Vuruşta Kırılır)
class HardWall(Wall):
    def __init__(self):
        self.health = 2 # 2 Kere patlamalı
        
    def get_color(self): 
        # Hasar alınca rengi koyulaşsın
        return "#800000" if self.health == 2 else "#CD5C5C"
        
    def is_breakable(self): return True
    
    def take_damage(self):
        """Hasar verir, kırılırsa True döner."""
        self.health -= 1
        return self.health <= 0