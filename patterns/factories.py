# patterns/factories.py
from interfaces import ThemeFactory
from models.walls import StoneWall, BrickWall, TreeWall

class CityThemeFactory(ThemeFactory):
    def create_hard_wall(self): return StoneWall()
    def create_soft_wall(self): return BrickWall()
    def get_background_color(self): return "#9E9E9E" # Beton Grisi

class ForestThemeFactory(ThemeFactory):
    def create_hard_wall(self): return StoneWall()
    def create_soft_wall(self): return TreeWall()
    def get_background_color(self): return "#4CAF50" # Çim Yeşili