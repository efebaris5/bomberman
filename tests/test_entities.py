import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.entities import Player, Enemy
from patterns.strategies import RandomStrategy

class TestEntities(unittest.TestCase):
    
    def setUp(self):
        """Her testten önce çalışır."""
        self.player = Player(1, 1)
        self.enemy = Enemy(5, 5, RandomStrategy())

    def test_player_initial_stats(self):
        """Oyuncu başlangıç değerleri doğru mu?"""
        self.assertEqual(self.player.health, 1, "Oyuncu 1 canla başlamalı.")
        self.assertTrue(self.player.is_alive, "Oyuncu canlı başlamalı.")

    def test_player_damage(self):
        """Oyuncu hasar aldığında canı azalıyor mu?"""
        initial_health = self.player.health
        self.player.take_damage()
        
        self.assertEqual(self.player.health, initial_health - 1, "Hasar alma fonksiyonu çalışmıyor.")
    
    def test_player_death(self):
        """Can 0 olunca oyuncu ölüyor mu?"""
        self.player.health = 1
        self.player.take_damage()
        
        self.assertEqual(self.player.health, 0)
        self.assertFalse(self.player.is_alive, "Can 0 olduğunda is_alive False olmalı.")

    def test_enemy_strategy(self):
        """Düşmanın bir stratejisi var mı?"""
        self.assertIsNotNone(self.enemy.strategy, "Düşmanın hareket stratejisi atanmamış.")

if __name__ == '__main__':
    unittest.main()