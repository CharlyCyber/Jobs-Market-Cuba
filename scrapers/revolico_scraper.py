from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class RevolicoScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("Revolico")
        self.url = Config.REVOLICO_URL
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting scraping from {self.source_name}")
        
        response = self._make_request(self.url)
        if not response:
            logger.error(f"Failed to fetch data from {self.source_name}")
            return []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            offers = self._parse_offers(soup)
            logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name}")
            return offers
        except Exception as e:
            logger.error(f"Error parsing {self.source_name}: {str(e)}")
            return []
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        job_listings = soup.find_all('li', class_='listing-item')
        
        if not job_listings:
            job_listings = soup.find_all('div', class_='ad-item')
        
        if not job_listings:
            job_listings = soup.find_all('article')
        
        logger.debug(f"Found {len(job_listings)} potential job listings")
        
        for job in job_listings:
            try:
                title_elem = job.find('a', class_='listing-title') or job.find('h2') or job.find('h3')
                if not title_elem:
                    title_elem = job.find('a')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                if link and not link.startswith('http'):
                    link = f"https://www.revolico.com{link}"
                
                description_elem = job.find('p', class_='description') or job.find('p')
                description = description_elem.get_text(strip=True) if description_elem else 'Sin descripción disponible'
                
                company_elem = job.find('span', class_='company') or job.find('div', class_='company')
                company = company_elem.get_text(strip=True) if company_elem else ''
                
                if title and link:
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
                    logger.debug(f"Parsed offer: {title}")
            
            except Exception as e:
                logger.debug(f"Error parsing individual job listing: {str(e)}")
                continue
        
        return offers
