import threading
import platform
import time
from interfaces import ISoundPlayer

class SoundManager(ISoundPlayer):
    def play_sound(self, sound_name):
        # Oyun donmasın diye sesi ayrı bir thread (iş parçacığı) içinde çalıyoruz
        threading.Thread(target=self._play_thread, args=(sound_name,), daemon=True).start()

    def _play_thread(self, sound_name):
        try:
            if platform.system() == "Windows":
                import winsound
                # Ses efektlerini frekans (Hz) ve süre (ms) ile oluşturuyoruz
                if sound_name == "BOMB":
                    winsound.Beep(1000, 100)  # İnce kısa bip (Bomba koyma)
                elif sound_name == "EXPLOSION":
                    winsound.Beep(150, 400)   # Kalın patlama sesi
                elif sound_name == "POWERUP":
                    winsound.Beep(2000, 100)  # Melodik bip
                    time.sleep(0.05)
                    winsound.Beep(2500, 100)
                elif sound_name == "WIN":
                    # Kazanma melodisi
                    winsound.Beep(500, 150)
                    winsound.Beep(1000, 150)
                    winsound.Beep(1500, 400)
                elif sound_name == "LOSE":
                    # Kaybetme sesi
                    winsound.Beep(600, 200)
                    winsound.Beep(400, 400)
            else:
                # Windows dışı sistemlerde konsola yazar (Hata vermemesi için)
                print(f"[SES] {sound_name} çalındı.")
        except Exception:
            pass # Ses hatası oyunu durdurmasın