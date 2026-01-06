from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class CucodersScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("CuCoders")
        self.url = Config.CUCODERS_URL
    
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
        
        job_listings = soup.find_all('div', class_='job-card')
        
        if not job_listings:
            job_listings = soup.find_all('article', class_='job')
        
        if not job_listings:
            job_listings = soup.find_all('div', class_='card')
        
        if not job_listings:
            job_listings = soup.select('.job, .position, article')
        
        logger.debug(f"Found {len(job_listings)} potential job listings")
        
        for job in job_listings:
            try:
                title_elem = job.find('h2') or job.find('h3') or job.find('a', class_='title')
                if not title_elem:
                    title_elem = job.find('a')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                if not link_elem:
                    link_elem = job.find('a')
                
                link = link_elem.get('href', '') if link_elem else ''
                
                if link and not link.startswith('http'):
                    link = f"https://cucoders.dev{link}"
                
                description_elem = job.find('div', class_='description') or job.find('p', class_='description') or job.find('p')
                description = description_elem.get_text(strip=True) if description_elem else 'Sin descripción disponible'
                
                company_elem = job.find('span', class_='company') or job.find('div', class_='company') or job.find('strong', class_='company')
                company = company_elem.get_text(strip=True) if company_elem else ''
                
                if title and link:
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
                    logger.debug(f"Parsed offer: {title}")
            
            except Exception as e:
                logger.debug(f"Error parsing individual job listing: {str(e)}")
                continue
        
        return offers
