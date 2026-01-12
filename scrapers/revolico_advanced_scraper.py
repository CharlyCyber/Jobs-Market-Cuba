from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.selenium_scraper import SeleniumBaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class RevolicoAdvancedScraper(SeleniumBaseScraper):
    
    def __init__(self):
        super().__init__("Revolico")
        self.url = Config.REVOLICO_URL
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting ADVANCED scraping from {self.source_name}")
        
        offers = []
        
        try:
            self._setup_driver()
            
            if self._make_request_selenium(self.url):
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                offers = self._parse_offers(soup)
                logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name}")
            else:
                logger.error(f"Failed to navigate to {self.url}")
        except Exception as e:
            logger.error(f"Error in Selenium scraping for {self.source_name}: {str(e)}")
        finally:
            self.cleanup()
        
        return offers
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        # Múltiples selectores para diferentes layouts de Revolico
        job_selectors = [
            ('li', 'listing-item'),
            ('div', 'ad-item'),
            ('article', 'ad-card'),
            ('div', 'job-item'),
            ('div', 'listing'),
        ]
        
        job_listings = []
        for tag, class_name in job_selectors:
            found = soup.find_all(tag, class_=class_name)
            if found:
                job_listings.extend(found)
                logger.debug(f"Found {len(found)} listings with {tag}.{class_name}")
        
        # Si no encontramos con clases específicas, buscar artículos genéricos
        if not job_listings:
            job_listings = soup.find_all('article')
            logger.debug(f"Found {len(job_listings)} generic articles")
        
        logger.info(f"Found total of {len(job_listings)} job listings to parse")
        
        for idx, job in enumerate(job_listings):
            try:
                # Múltiples selectores para títulos
                title_elem = None
                title_selectors = [
                    ('a', 'listing-title'),
                    ('h2', None),
                    ('h3', None),
                    ('div', 'title'),
                    ('a', 'ad-title'),
                    ('a', None),  # Último recurso: cualquier <a>
                ]
                
                for tag, class_name in title_selectors:
                    if class_name:
                        title_elem = job.find(tag, class_=class_name)
                    else:
                        title_elem = job.find(tag)
                    if title_elem:
                        break
                
                if not title_elem:
                    logger.debug(f"No title element found in listing {idx}")
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                if not link:
                    # Buscar cualquier link dentro del elemento
                    link_elem = job.find('a')
                    if link_elem:
                        link = link_elem.get('href', '')
                
                if link and not link.startswith('http'):
                    if link.startswith('/'):
                        link = f"https://www.revolico.com{link}"
                    else:
                        link = f"https://www.revolico.com/{link}"
                
                # Múltiples selectores para descripción
                description = "Descripción no disponible"
                desc_selectors = [
                    ('p', 'description'),
                    ('div', 'description'),
                    ('p', None),
                    ('div', 'text'),
                    ('div', 'content'),
                ]
                
                for tag, class_name in desc_selectors:
                    if class_name:
                        desc_elem = job.find(tag, class_=class_name)
                    else:
                        desc_elem = job.find(tag)
                    if desc_elem:
                        description = desc_elem.get_text(strip=True)
                        break
                
                # Múltiples selectores para empresa
                company = ""
                company_selectors = [
                    ('span', 'company'),
                    ('div', 'company'),
                    ('span', 'advertiser'),
                    ('div', 'advertiser'),
                    ('span', None),
                ]
                
                for tag, class_name in company_selectors:
                    if class_name:
                        company_elem = job.find(tag, class_=class_name)
                    else:
                        company_elem = job.find(tag)
                    if company_elem:
                        company_text = company_elem.get_text(strip=True)
                        if len(company_text) < 50:  # Evitar textos largos
                            company = company_text
                            break
                
                if title and link:
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
                    if len(offers) <= 5:  # Solo log los primeros 5 para no saturar
                        logger.debug(f"Parsed offer {len(offers)}: {title[:50]}...")
                
            except Exception as e:
                logger.debug(f"Error parsing individual job listing {idx}: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(offers)} valid offers from {len(job_listings)} listings")
        return offers
