# interfaces.py
import abc

# Temel Oyun Nesnesi
class GameObject:
    def __init__(self, x, y):
        self._x = x
        self._y = y
    
    @property
    def x(self): return self._x
    @x.setter
    def x(self, value): self._x = value
    
    @property
    def y(self): return self._y
    @y.setter
    def y(self, value): self._y = value

# Observer Pattern Arayüzleri
class Observer(abc.ABC):
    @abc.abstractmethod
    def update(self, event_type, data): pass

class Subject:
    def __init__(self):
        self._observers = []
    def add_observer(self, observer):
        self._observers.append(observer)
    def notify(self, event_type, data):
        for obs in self._observers:
            obs.update(event_type, data)

# Decorator için Oyuncu Arayüzü
class IPlayer(abc.ABC):
    @property
    @abc.abstractmethod
    def x(self): pass
    @property
    @abc.abstractmethod
    def y(self): pass
    @abc.abstractmethod
    def get_bomb_power(self): pass
    @abc.abstractmethod
    def get_image_key(self): pass
    @abc.abstractmethod
    def set_pos(self, x, y): pass
    @abc.abstractmethod
    def kill(self): pass
    @property
    @abc.abstractmethod
    def is_alive(self): pass

# Strategy Pattern Arayüzü
class MoveStrategy(abc.ABC):
    @abc.abstractmethod
    def move(self, enemy_pos, player_pos, grid): pass

# Factory Pattern Arayüzleri
class Wall(abc.ABC):
    @abc.abstractmethod
    def get_color(self): pass
    @abc.abstractmethod
    def is_breakable(self): pass

class ThemeFactory(abc.ABC):
    @abc.abstractmethod
    def create_hard_wall(self) -> Wall: pass   # Kırılmaz (Çerçeve)
    @abc.abstractmethod
    def create_soft_wall(self) -> Wall: pass   # Tek vuruşluk
    @abc.abstractmethod
    def create_durable_wall(self) -> Wall: pass # Çok vuruşluk 
    @abc.abstractmethod
    def get_background_color(self) -> str: pass