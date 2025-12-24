from interfaces import Wall

# --- TEMEL SINIFLAR (Base Classes) ---
class HardWall(Wall):
    """Tüm kırılmaz duvarların atası."""
    def get_color(self):
        return "grey"
    
    def is_breakable(self):
        return False

    def get_image_key(self):
        return "wall_hard"

class SoftWall(Wall):
    """Tüm kırılabilir duvarların atası."""
    def get_color(self):
        return "#8B4513"  # Kahverengi
    
    def is_breakable(self):
        return True

    def get_image_key(self):
        return "wall_soft"

class DurableWall(Wall):
    """2 vuruşta kırılan özel duvar."""
    def __init__(self):
        self.health = 2 
        
    def get_color(self):
        return "#556B2F" # Koyu zeytin yeşili
    
    def is_breakable(self):
        return True

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def get_image_key(self):
        return "wall_durable"

# --- TEMA İÇİN GEREKLİ SINIFLAR (HATA VERENLER) ---
# Factories.py dosyasının çalışması için bu sınıfların burada olması şart.
# Hepsi yukarıdaki HardWall veya SoftWall'dan miras alarak özelliklerini korur.

class StoneWall(HardWall):
    """Forest Teması: Kırılmaz Duvar"""
    def get_image_key(self):
        return "wall_hard"

class TreeWall(SoftWall):
    """Forest Teması: Kırılabilir Duvar"""
    def get_image_key(self):
        return "wall_soft"

class BrickWall(SoftWall):
    """City Teması: Kırılabilir Duvar (Tuğla)"""
    def get_color(self):
        return "#B22222" # FireBrick Rengi
    def get_image_key(self):
        return "wall_soft"

class SandWall(SoftWall):
    """Desert Teması: Kırılabilir Duvar (Kum Taşı)"""
    def get_color(self):
        return "#F4A460" # SandyBrown Rengi
    def get_image_key(self):
        return "wall_soft"
        
# City Teması için Kırılmaz Duvar gerekirse (Metal vb.)
class MetalWall(HardWall):
    def get_image_key(self):
        return "wall_hard"