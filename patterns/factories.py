from interfaces import ThemeFactory
from models.walls import StoneWall, BrickWall, TreeWall, SandWall, HardWall, DurableWall

# --- FLYWEIGHT FACTORY ---
class WallFlyweightFactory:
    """
    Flyweight Deseni: Aynı türdeki duvarları tekrar tekrar oluşturmak yerine
    hafızada tutar ve oradan verir.
    """
    _walls = {}

    @staticmethod
    def get_wall(wall_class):
        # Eğer bu sınıf tipinden bir duvar daha önce üretilmediyse üret ve sakla
        if wall_class not in WallFlyweightFactory._walls:
            WallFlyweightFactory._walls[wall_class] = wall_class()
        
        # Saklanan duvarı (referansı) döndür
        return WallFlyweightFactory._walls[wall_class]

# --- TEMA FABRİKALARI (ABSTRACT FACTORY) ---

class ForestThemeFactory(ThemeFactory):
    def create_hard_wall(self):
        # HardWall değişmez, Flyweight kullanabiliriz
        return WallFlyweightFactory.get_wall(StoneWall)
    
    def create_soft_wall(self):
        # SoftWall tek vuruşluktur, Flyweight kullanabiliriz
        return WallFlyweightFactory.get_wall(TreeWall)

    def create_durable_wall(self):
        # DİKKAT: DurableWall'ın 'can' (health) değeri vardır.
        # Flyweight kullanırsak birine vurunca hepsi hasar alır.
        # O yüzden her seferinde YENİ bir tane oluşturuyoruz.
        return DurableWall()

    def get_background_color(self):
        return "#355E3B"

class CityThemeFactory(ThemeFactory):
    def create_hard_wall(self):
        return WallFlyweightFactory.get_wall(HardWall)
    
    def create_soft_wall(self):
        return WallFlyweightFactory.get_wall(BrickWall)

    def create_durable_wall(self):
        # Yeni nesne (Instance)
        return DurableWall()

    def get_background_color(self):
        return "#2F4F4F"

class DesertThemeFactory(ThemeFactory):
    def create_hard_wall(self):
        return WallFlyweightFactory.get_wall(HardWall)
    
    def create_soft_wall(self):
        return WallFlyweightFactory.get_wall(SandWall)

    def create_durable_wall(self):
        # Yeni nesne (Instance)
        return DurableWall()

    def get_background_color(self):
        return "#DEB887"