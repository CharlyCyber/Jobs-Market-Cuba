import pytest
from scrapers.revolico_scraper import RevolicoScraper
from scrapers.cubisima_scraper import CubisimaScraper
from scrapers.cucoders_scraper import CucodersScraper


class TestScrapers:
    
    def test_revolico_scraper_initialization(self):
        scraper = RevolicoScraper()
        assert scraper.source_name == "Revolico"
        assert scraper.url is not None
    
    def test_cubisima_scraper_initialization(self):
        scraper = CubisimaScraper()
        assert scraper.source_name == "Cubisima"
        assert len(scraper.urls) == 3
    
    def test_cucoders_scraper_initialization(self):
        scraper = CucodersScraper()
        assert scraper.source_name == "CuCoders"
        assert scraper.url is not None
    
    def test_scraper_create_offer(self):
        scraper = RevolicoScraper()
        offer = scraper._create_offer(
            title="Test Job",
            company="Test Company",
            description="Test Description",
            link="http://example.com"
        )
        
        assert offer['title'] == "Test Job"
        assert offer['company'] == "Test Company"
        assert offer['description'] == "Test Description"
        assert offer['link'] == "http://example.com"
        assert offer['source'] == "Revolico"
    
    def test_scraper_create_offer_no_company(self):
        scraper = RevolicoScraper()
        offer = scraper._create_offer(
            title="Test Job",
            company="",
            description="Test Description",
            link="http://example.com"
        )
        
        assert offer['company'] == "No especificada"


class TestScraperIntegration:
    
    @pytest.mark.asyncio
    async def test_scraper_manager_initialization(self):
        from scrapers.scraper_manager import ScraperManager
        
        manager = ScraperManager()
        assert len(manager.scrapers) == 3
        assert manager.job_filter is not None
