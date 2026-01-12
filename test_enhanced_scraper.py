#!/usr/bin/env python3

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.revolico_enhanced_scraper import RevolicoEnhancedScraper
from scrapers.cubisima_scraper import CubisimaScraper
from scrapers.cucoders_scraper import CucodersScraper
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_revolico():
    """Prueba exhaustiva de Revolico con el scraper enhanced"""
    print("=" * 70)
    print("TESTING REVOLICO SCRAPER ENHANCED")
    print("=" * 70)
    
    scraper = RevolicoEnhancedScraper()
    
    try:
        print(f"\n1. URL objetivo: {scraper.url}")
        print("2. Iniciando scraping con técnicas anti-detection...")
        
        offers = scraper.scrape()
        
        print(f"\n3. Resultados:")
        print(f"   - Ofertas encontradas: {len(offers)}")
        
        if offers:
            print(f"\n4. Primeras 3 ofertas:")
            for i, offer in enumerate(offers[:3], 1):
                print(f"\n   Oferta {i}:")
                print(f"   - Título: {offer['title'][:80]}...")
                print(f"   - Empresa: {offer['company'] or 'N/A'}")
                print(f"   - Link: {offer['link'][:60]}...")
                print(f"   - Descripción: {offer['description'][:100]}...")
        else:
            print(f"\n4. WARNING: No se encontraron ofertas")
            print("   Posibles causas:")
            print("   - La página está bloqueando completamente")
            print("   - El HTML recibido es diferente al esperado")
            print("   - Las ofertas están en formato JS que no podemos parsear")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


def test_all_platforms():
    """Prueba rápida de todas las plataformas"""
    print("\n" + "=" * 70)
    print("TESTING ALL PLATFORMS")
    print("=" * 70)
    
    scrapers = [
        ("Revolico", RevolicoEnhancedScraper()),
        ("Cubisima", CubisimaScraper()),
        ("CuCoders", CucodersScraper())
    ]
    
    total_offers = 0
    
    for name, scraper in scrapers:
        print(f"\nTesting {name}...")
        try:
            offers = scraper.scrape()
            print(f"  ✓ Ofertas: {len(offers)}")
            total_offers += len(offers)
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print(f"\n{'=' * 70}")
    print(f"TOTAL DE OFERTAS ENCONTRADAS: {total_offers}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    test_revolico()
    test_all_platforms()
