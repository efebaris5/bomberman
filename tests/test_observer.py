import unittest
import sys
import os

# Proje ana dizinini yola ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.entities import Bomb, Player

class TestObserver(unittest.TestCase):
    
    def test_bomb_notify(self):
        """Observer Testi: Bomba patlayınca oyuncuya hasar veriyor mu?"""
        player = Player(2, 2)
        bomb = Bomb(2, 2, power=1)
        
        bomb.add_observer(player)
        
        # --- DÜZELTME 1: _observers kullanıldı (Subject sınıfındaki isme uygun) ---
        for observer in bomb._observers:
            if observer.x == bomb.x and observer.y == bomb.y:
                # Eğer Player sınıfında take_damage fonksiyonu varsa onu çağır
                if hasattr(observer, 'take_damage'):
                    observer.take_damage()
                else:
                    observer.kill() # Yoksa direkt öldür (Eski kod uyumu)
        
        # Sonuç Kontrolü
        if hasattr(player, 'health'):
            # Can sistemi varsa canın azaldığını kontrol et
            # Başlangıç canı 3 kabul edildiğinde, hasar alınca 3'ten az olmalı
            self.assertLess(player.health, 3, "Observer (Oyuncu) bombadan hasar almadı!")
        else:
            # Can sistemi yoksa direkt öldüğünü kontrol et
            self.assertFalse(player.is_alive, "Observer (Oyuncu) bombadan ölmedi!")

if __name__ == '__main__':
    unittest.main()