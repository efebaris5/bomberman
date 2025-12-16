# patterns/factories.py
from interfaces import ThemeFactory
from models.walls import StoneWall, BrickWall, TreeWall, SandWall, HardWall

class CityThemeFactory(ThemeFactory):
    def create_hard_wall(self): return StoneWall()
    def create_soft_wall(self): return BrickWall()
    def create_durable_wall(self): return HardWall() # Şehirde de sert duvar olabilir
    def get_background_color(self): return "#9E9E9E"

class ForestThemeFactory(ThemeFactory):
    def create_hard_wall(self): return StoneWall()
    def create_soft_wall(self): return TreeWall()
    def create_durable_wall(self): return HardWall()
    def get_background_color(self): return "#4CAF50"

# --- YENİ EKLENEN TEMA ---
class DesertThemeFactory(ThemeFactory):
    def create_hard_wall(self): return StoneWall()
    def create_soft_wall(self): return SandWall()
    def create_durable_wall(self): return HardWall()
    def get_background_color(self): return "#F4A460" # SandyBrown