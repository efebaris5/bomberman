from interfaces import IPlayer, Observer

class PlayerDecorator(IPlayer, Observer):
    def __init__(self, wrapped_player: IPlayer):
        self._wrapped = wrapped_player
    
    @property
    def x(self): return self._wrapped.x
    @property
    def y(self): return self._wrapped.y
    
    def set_pos(self, x, y): self._wrapped.set_pos(x, y)
    def kill(self): self._wrapped.kill()
    
    @property
    def is_alive(self): return self._wrapped.is_alive

    def get_bomb_power(self):
        return self._wrapped.get_bomb_power()
    
    # --- YENİ: Delegate (Aktarma) ---
    def get_max_bombs(self):
        return self._wrapped.get_max_bombs()
    # --------------------------------
    
    def get_image_key(self):
        return self._wrapped.get_image_key()
    
    def update(self, event_type, data):
        if isinstance(self._wrapped, Observer):
            self._wrapped.update(event_type, data)

# Mevcut Power-up
class BombPowerUp(PlayerDecorator):
    def get_bomb_power(self):
        return self._wrapped.get_bomb_power() + 1

# --- YENİ: Bomba Sayısı Artırma ---
class BombCountPowerUp(PlayerDecorator):
    def get_max_bombs(self):
        return self._wrapped.get_max_bombs() + 1

# --- YENİ: Hız Artırma (Göstermelik/Bonus) ---
class SpeedPowerUp(PlayerDecorator):
    # Bu sınıf şimdilik sadece görseli veya türü değiştirir
    # İleride hız mantığı eklenirse buraya kod yazılır.
    pass