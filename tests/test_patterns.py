import unittest
import sys
import os

# Proje ana dizinini yola ekle (Import hatalarını önlemek için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseRepository
from patterns.factories import ForestThemeFactory, CityThemeFactory
from models.walls import Wall

class TestPatterns(unittest.TestCase):
    
    def test_singleton_database(self):
        """Singleton Testi: Veritabanı sınıfından iki nesne üretilse bile bunlar aynı mı?"""
        db1 = DatabaseRepository()
        db2 = DatabaseRepository()
        
        # Bellek adresleri (instance'lar) aynı olmalı
        self.assertIs(db1, db2, "DatabaseRepository Singleton kuralına uymuyor!")
        
    def test_factory_creation(self):
        """Factory Testi: Fabrikalar doğru duvar nesnelerini üretiyor mu?"""
        forest_factory = ForestThemeFactory()
        city_factory = CityThemeFactory()
        
        # Orman fabrikası duvar üretmeli
        wall1 = forest_factory.create_hard_wall()
        self.assertIsInstance(wall1, Wall, "ForestFactory geçerli bir duvar üretmedi.")
        self.assertFalse(wall1.is_breakable(), "Hard Wall kırılabilir olmamalı.")
        
        # Şehir fabrikası da duvar üretmeli ama rengi/teması farklı olabilir
        wall2 = city_factory.create_soft_wall()
        self.assertIsInstance(wall2, Wall)
        self.assertTrue(wall2.is_breakable(), "Soft Wall kırılabilir olmalı.")

if __name__ == '__main__':
    unittest.main()