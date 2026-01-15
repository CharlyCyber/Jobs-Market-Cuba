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
                self.url, 
                headers=headers, 
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data from {self.source_name}, status: {response.status_code}")
                return []
            
            # Force UTF-8 encoding
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            offers = self._parse_offers(soup)
            logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name}")
            return offers
            
        except Exception as e:
            logger.error(f"Error in direct scraping for {self.source_name}: {str(e)}")
            
            # Fallback to base scraper method
            logger.info("Falling back to base scraper method")
            return self._scrape_with_base_method()
    
    def _scrape_with_base_method(self) -> List[Dict[str, str]]:
        """Fallback scraping using the base scraper method"""
        response = self._make_request(self.url)
        if not response:
            logger.error(f"Failed to fetch data from {self.source_name}")
            return []
        
        try:
            # Handle encoding properly
            if response.encoding.lower() not in ['utf-8', 'utf8']:
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            offers = self._parse_offers(soup)
            logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name}")
            return offers
        except Exception as e:
            logger.error(f"Error parsing {self.source_name}: {str(e)}")
            return []
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        # CuCoders uses Astro framework with dynamic content
        # Look for job listings in the actual structure observed
        # Jobs are in divs with 'inline-grid' class that contain links with '/empleos/YYYY-MM-DD/'
        
        # Debug: Check if soup was parsed correctly
        total_links = len(soup.find_all('a'))
        logger.debug(f"Total links found in soup: {total_links}")
        
        # First, find all links that match the job pattern
        import re
        job_links = soup.find_all('a', href=lambda x: x and '/empleos/' in x and re.search(r'\d{4}-\d{2}-\d{2}', x))
        
        logger.debug(f"Found {len(job_links)} job links")
        
        # Debug: Show first few hrefs to verify
        for i, link in enumerate(job_links[:3]):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:30]
            logger.debug(f"Job link {i+1}: {href} -> {text}...")
        
        if job_links:
            # Group links by their parent container to avoid duplicates
            seen_containers = set()
            
            for link in job_links:
                try:
                    # Get the container div that holds this job
                    container = link.find_parent('div', class_='inline-grid')
                    if not container:
                        container = link.find_parent('div', class_=lambda x: x and 'inline-grid' in x if x else False)
                    
                    if container:
                        container_id = str(container)
                        if container_id in seen_containers:
                            continue
                        seen_containers.add(container_id)
                        
                        offer = self._extract_job_info(container)
                        if offer:
                            offers.append(offer)
                            logger.debug(f"Parsed offer: {offer['title']}")
                
                except Exception as e:
                    logger.debug(f"Error parsing job container: {str(e)}")
                    continue
        
        logger.debug(f"Total offers extracted: {len(offers)}")
        return offers
    
    def _extract_job_info(self, job_element) -> Dict[str, str]:
        """Extract job information from a job listing element"""
        try:
            # Strategy 1: Find the main title link (usually the first one with font-semibold)
            title_elem = job_element.find('a', class_=lambda x: x and 'font-semibold' in ' '.join(x) if x else False)
            
            if not title_elem:
                # Fallback: Find any link that matches the job URL pattern
                import re
                title_elem = job_element.find('a', href=lambda x: x and '/empleos/' in x and re.search(r'\d{4}-\d{2}-\d{2}', x))
            
            if not title_elem:
                # Final fallback: Look for any link
                title_elem = job_element.find('a')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Extract the link
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://cucoders.dev{link}"
            
            # Extract description - look for the second link or content elements
            description_elem = None
            
            # Try to find description in elements with line-clamp-3 class
            description_elem = job_element.find('a', class_=lambda x: x and 'line-clamp-3' in ' '.join(x) if x else False)
            
            if not description_elem:
                # Try to find description in other links
                all_links = job_element.find_all('a')
                for link_elem in all_links:
                    if link_elem != title_elem:  # Skip the title link
                        text = link_elem.get_text(strip=True)
                        # Description is usually longer and not the title
                        if text and len(text) > 30 and text != title:
                            description_elem = link_elem
                            break
            
            if not description_elem:
                # Last resort: extract from paragraph or div elements
                desc_parts = []
                for elem in job_element.find_all(['p', 'div']):
                    text = elem.get_text(strip=True)
                    # Avoid title and very short text
                    if text and len(text) > 20 and text != title and not any(keyword in text.lower() for keyword in ['tiempo', 'parcial', 'completo', 'freelance', 'remoto', 'presencial']):
                        desc_parts.append(text)
                description = ' '.join(desc_parts)[:300]
            else:
                description = description_elem.get_text(strip=True)
            
            if not description:
                description = 'Sin descripción disponible'
            
            # Extract company - CuCoders doesn't always show explicit company
            company = ''
            
            # Try to find company in various patterns
            desc_text = description.lower()
            
            # Look for company patterns in description
            import re
            company_patterns = [
                r'en\s+([A-Za-z\s]{3,25})',
                r'para\s+([A-Za-z\s]{3,25})',
                r'@([A-Za-z\s]{3,25})',
                r'por\s+([A-Za-z\s]{3,25})',
                r'busca\s+([A-Za-z\s]{3,25})',
                r'somos\s+([A-Za-z\s]{3,25})',
                r'empresa\s+([A-Za-z\s]{3,25})'
            ]
            
            for pattern in company_patterns:
                match = re.search(pattern, desc_text)
                if match:
                    company = match.group(1).strip()
                    # Clean up the company name
                    company = re.sub(r'[^\w\s]', '', company).strip()
                    if len(company) > 2:
                        break
            
            # If still no company, try to extract from URL slug
            if not company and '/empleos/' in link:
                url_parts = link.split('/empleos/')[-1].split('/')
                if len(url_parts) > 1:
                    slug = url_parts[-1]
                    # Convert slug to readable company name (basic approach)
                    company = slug.replace('-', ' ').title()
                    # Take only first few words as company name
                    company_words = company.split()[:3]
                    company = ' '.join(company_words)
            
            # Final fallback
            if not company:
                company = 'No especificada'
            
            if title and link:
                return self._create_offer(title, company, description, link)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting job info: {str(e)}")
            return None
