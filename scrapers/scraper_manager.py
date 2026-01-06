from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapers.revolico_scraper import RevolicoScraper
from scrapers.revolico_enhanced_scraper import RevolicoEnhancedScraper
from scrapers.cubisima_scraper import CubisimaScraper
from scrapers.cucoders_scraper import CucodersScraper
from filters.job_filter import JobFilter
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class ScraperManager:
    
    def __init__(self):
        # Usar scraper enhanced (httpx avanzado anti-detection) por defecto
        # Es más rápido y no requiere Chrome instalado
        revolico_scraper = RevolicoEnhancedScraper()
        
        self.scrapers = [
            revolico_scraper,
            CubisimaScraper(),
            CucodersScraper()
        ]
        self.job_filter = JobFilter()
        logger.info(f"Initialized ScraperManager with {len(self.scrapers)} scrapers (Using Enhanced Anti-Detection)")
    
    async def scrape_all(self) -> List[Dict[str, str]]:
        logger.info("Starting parallel scraping from all sources")
        
        loop = asyncio.get_event_loop()
        all_offers = []
        
        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            future_to_scraper = {
                executor.submit(scraper.scrape): scraper 
                for scraper in self.scrapers
            }
            
            for future in as_completed(future_to_scraper):
                scraper = future_to_scraper[future]
                try:
                    offers = future.result()
                    all_offers.extend(offers)
                    logger.info(f"{scraper.source_name} returned {len(offers)} offers")
                except Exception as e:
                    logger.error(f"Error scraping {scraper.source_name}: {str(e)}")
        
        logger.info(f"Total offers scraped (before filtering): {len(all_offers)}")
        
        filtered_offers = self.job_filter.filter_offers(all_offers)
        
        logger.info(f"Total offers after filtering: {len(filtered_offers)}")
        
        return filtered_offers
    
    def scrape_all_sync(self) -> List[Dict[str, str]]:
        logger.info("Starting sequential scraping from all sources")
        all_offers = []
        
        for scraper in self.scrapers:
            try:
                offers = scraper.scrape()
                all_offers.extend(offers)
                logger.info(f"{scraper.source_name} returned {len(offers)} offers")
            except Exception as e:
                logger.error(f"Error scraping {scraper.source_name}: {str(e)}")
        
        logger.info(f"Total offers scraped (before filtering): {len(all_offers)}")
        
        filtered_offers = self.job_filter.filter_offers(all_offers)
        
        logger.info(f"Total offers after filtering: {len(filtered_offers)}")
        
        return filtered_offers
