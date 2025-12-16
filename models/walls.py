# models/walls.py
from interfaces import Wall

class StoneWall(Wall):
    def get_color(self): return "#444444"
    def is_breakable(self): return False

class BrickWall(Wall):
    def get_color(self): return "#A0522D"
    def is_breakable(self): return True

class TreeWall(Wall):
    def get_color(self): return "#228B22"
    def is_breakable(self): return True