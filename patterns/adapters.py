import winsound
from interfaces import ISoundPlayer

# Adaptee (Var olan, uyumsuz yapı)
# Winsound zaten var ama biz kendi arayüzümüze uyduracağız.

class WindowsSoundAdapter(ISoundPlayer):
    """Adapter Pattern: Windows ses sistemini oyunun arayüzüne uyarlar."""
    def play_sound(self, sound_name):
        # Ses dosyalarının 'assets/sounds/' klasöründe olduğunu varsayalım
        # sound_name: 'explosion', 'move', 'place_bomb'
        try:
            # Örnek: assets/sounds/explosion.wav
            path = f"assets/sounds/{sound_name}.wav"
            # SND_ASYNC: Oyun donmasın diye asenkron çalar
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Ses hatası: {e}")