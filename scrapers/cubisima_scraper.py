from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class CubisimaScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("Cubisima")
        self.urls = [
            Config.CUBISIMA_MARKETING_URL,
            Config.CUBISIMA_DESIGN_URL,
            Config.CUBISIMA_IT_URL
        ]
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting scraping from {self.source_name}")
        all_offers = []
        
        for url in self.urls:
            logger.debug(f"Scraping URL: {url}")
            response = self._make_request(url)
            
            if not response:
                logger.warning(f"Failed to fetch data from {url}")
                continue
            
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                offers = self._parse_offers(soup)
                all_offers.extend(offers)
                logger.info(f"Scraped {len(offers)} offers from {url}")
            except Exception as e:
                logger.error(f"Error parsing {url}: {str(e)}")
                continue
        
        logger.info(f"Successfully scraped {len(all_offers)} total offers from {self.source_name}")
        return all_offers
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        job_listings = soup.find_all('div', class_='job-listing')
        
        if not job_listings:
            job_listings = soup.find_all('div', class_='offer-item')
        
        if not job_listings:
            job_listings = soup.find_all('article', class_='job')
        
        if not job_listings:
            job_listings = soup.find_all('div', class_='row')
        
        logger.debug(f"Found {len(job_listings)} potential job listings")
        
        for job in job_listings:
            try:
                title_elem = job.find('h3') or job.find('h2') or job.find('h4')
                if title_elem:
                    link_elem = title_elem.find('a') or title_elem.find_parent('a')
                else:
                    link_elem = job.find('a', class_='job-title') or job.find('a')
                
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                
                if link and not link.startswith('http'):
                    link = f"https://www.cubisima.com{link}"
                
                description_elem = job.find('div', class_='description') or job.find('p', class_='description') or job.find('p')
                description = description_elem.get_text(strip=True) if description_elem else 'Sin descripción disponible'
                
                company_elem = job.find('span', class_='company') or job.find('div', class_='company-name') or job.find('strong')
                company = company_elem.get_text(strip=True) if company_elem else ''
                
                if title and link:
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
                    logger.debug(f"Parsed offer: {title}")
            
            except Exception as e:
                logger.debug(f"Error parsing individual job listing: {str(e)}")
                continue
        
        return offers
