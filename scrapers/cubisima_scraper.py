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
            
            # Use direct request approach to avoid encoding issues
            import requests
            from bot.config import Config
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=Config.REQUEST_TIMEOUT
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}, status: {response.status_code}")
                    continue
                
                # Force UTF-8 encoding
                response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.text, 'html.parser')
                offers = self._parse_offers(soup)
                all_offers.extend(offers)
                logger.info(f"Scraped {len(offers)} offers from {url}")
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        logger.info(f"Successfully scraped {len(all_offers)} total offers from {self.source_name}")
        return all_offers
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        # Multiple strategies to find job listings
        selectors = [
            'div.job-listing',
            'div.offer-item',
            'article.job',
            'div.row',
            'div.listing-item',
            '.job-item',
            '.offer',
            'li.resultado',
            'div.resultado',
            '.list-item'
        ]
        
        job_listings = []
        for selector in selectors:
            job_listings = soup.select(selector)
            if job_listings:
                logger.debug(f"Found {len(job_listings)} potential job listings using selector: {selector}")
                break
        
        if not job_listings:
            # Try finding by common job-related text patterns
            potential_jobs = soup.find_all(['div', 'li', 'article'])
            for element in potential_jobs:
                text = element.get_text().lower()
                if any(keyword in text for keyword in ['empleo', 'trabajo', 'job', 'oferta', 'contrat', 'marketing', 'diseño', 'it']):
                    job_listings.append(element)
            
            logger.debug(f"Found {len(job_listings)} potential jobs by text pattern")
        
        for job in job_listings:
            try:
                offer = self._extract_job_info(job)
                if offer:
                    offers.append(offer)
                    logger.debug(f"Parsed offer: {offer['title']}")
            
            except Exception as e:
                logger.debug(f"Error parsing individual job listing: {str(e)}")
                continue
        
        return offers
    
    def _extract_job_info(self, job_element) -> Dict[str, str]:
        """Extract job information from a job listing element"""
        try:
            # Try multiple strategies to find title and link
            title_elem = None
            link = None
            
            # Strategy 1: Look for headings with links
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                title_elem = job_element.find(tag)
                if title_elem:
                    link_elem = title_elem.find('a')
                    if link_elem:
                        title_elem = link_elem
                        link = link_elem.get('href', '')
                        break
                    else:
                        # Look for parent link
                        parent_link = title_elem.find_parent('a')
                        if parent_link:
                            title_elem = parent_link
                            link = parent_link.get('href', '')
                            break
            
            # Strategy 2: Look for anchor tags directly
            if not title_elem:
                link_elem = job_element.find('a', class_=['job-title', 'title', 'offer-title'])
                if not link_elem:
                    link_elem = job_element.find('a')
                
                if link_elem:
                    title_elem = link_elem
                    link = link_elem.get('href', '')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Handle relative URLs
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = f"https://www.cubisima.com{link}"
                else:
                    link = f"https://www.cubisima.com/{link}"
            
            # Extract description
            desc_selectors = [
                'div.description',
                'p.description',
                '.description',
                'div.content',
                'p',
                '.text',
                '.resumen'
            ]
            
            description = ''
            for selector in desc_selectors:
                desc_elem = job_element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    break
            
            if not description:
                # Fallback: get text content excluding title
                text_parts = job_element.get_text().split('\n')
                description = ' '.join([part.strip() for part in text_parts if part.strip() and part.strip() != title])[:200]
            
            # Extract company
            company_selectors = [
                'span.company',
                'div.company',
                '.company-name',
                '.empresa',
                'strong',
                '.organization'
            ]
            
            company = ''
            for selector in company_selectors:
                company_elem = job_element.select_one(selector)
                if company_elem:
                    company = company_elem.get_text(strip=True)
                    break
            
            if not company:
                # Try to extract from title if it contains company info
                title_words = title.split()
                if len(title_words) > 2:
                    # Look for common company patterns
                    for i in range(min(3, len(title_words) - 1)):
                        potential_company = ' '.join(title_words[i:i+2])
                        if potential_company not in ['Ofertas de', 'Trabajos en', 'Marketing', 'Diseño']:
                            company = potential_company
                            break
            
            if title and link:
                return self._create_offer(title, company, description, link)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting job info: {str(e)}")
            return None
