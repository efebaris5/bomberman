# patterns/factories.py
from interfaces import ThemeFactory
from models.walls import StoneWall, BrickWall, TreeWall, SandWall, HardWall



class WallFlyweightFactory:
    """Flyweight Deseni: Duvar nesnelerini önbellekte tutar."""
    _walls = {}

    @staticmethod
    def get_wall(wall_class):
        # Eğer bu duvar türü daha önce üretildiyse, hafızadakini döndür.
        if wall_class not in WallFlyweightFactory._walls:
            WallFlyweightFactory._walls[wall_class] = wall_class()
        return WallFlyweightFactory._walls[wall_class]
    
class CityThemeFactory(ThemeFactory):
    def create_hard_wall(self): 
        # return StoneWall() YERİNE:
        return WallFlyweightFactory.get_wall(StoneWall)
        
    def create_soft_wall(self): 
        # return BrickWall() YERİNE:
        return WallFlyweightFactory.get_wall(BrickWall)
        
    def create_durable_wall(self): 
        return HardWall() # Bu flyweight olamaz çünkü canı (state) var.
    
    def get_background_color(self): return "#9E9E9E"

class ForestThemeFactory(ThemeFactory):
    def create_hard_wall(self): 
        # return StoneWall() YERİNE:
        return WallFlyweightFactory.get_wall(StoneWall)
        
    def create_soft_wall(self): 
        # return BrickWall() YERİNE:
        return WallFlyweightFactory.get_wall(BrickWall)
        
    def create_durable_wall(self): 
        return HardWall() # Bu flyweight olamaz çünkü canı (state) var.
    
    def get_background_color(self): return "#146E19"

# --- YENİ EKLENEN TEMA ---
class DesertThemeFactory(ThemeFactory):
    def create_hard_wall(self): 
        # return StoneWall() YERİNE:
        return WallFlyweightFactory.get_wall(StoneWall)
        
    def create_soft_wall(self): 
        # return BrickWall() YERİNE:
        return WallFlyweightFactory.get_wall(BrickWall)
        
    def create_durable_wall(self): 
        return HardWall() # Bu flyweight olamaz çünkü canı (state) var.
    
    def get_background_color(self): return "#F4A460" # SandyBrown