from typing import List, Dict
from bs4 import BeautifulSoup
import time
import random
import json
from scrapers.base_scraper import BaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)

# Importar undetected-chromedriver (mejor que Selenium normal)
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium_stealth import stealth
    UNDETECTED_CHROMEDRIVER_AVAILABLE = True
    logger.info("✓ Undetected ChromeDriver disponible")
except ImportError as e:
    UNDETECTED_CHROMEDRIVER_AVAILABLE = False
    logger.warning(f"✗ Undetected ChromeDriver no disponible: {e}")


class RevolicoScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("Revolico", use_cache=True, use_proxy=True)
        self.url = Config.REVOLICO_URL
        self.driver = None
    
    def _setup_undetected_chrome(self):
        """Setup Undetected ChromeDriver con configuración anti-detección"""
        if not UNDETECTED_CHROMEDRIVER_AVAILABLE:
            return False
        
        try:
            options = uc.ChromeOptions()
            
            # Configuración básica
            options.add_argument('--headless=new')  # Nuevo headless más indetectable
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-web-security')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-gpu')
            
            # Configurar proxy si está disponible
            if self.use_proxy and self.proxy_rotator:
                proxy = self.proxy_rotator.get_next_proxy()
                if proxy:
                    options.add_argument(f'--proxy-server={proxy.get("http", "")}')
                    logger.info(f"🌐 Usando proxy en Chrome: {proxy.get('http', '')[:30]}...")
            
            # Inicializar undetected-chromedriver
            self.driver = uc.Chrome(options=options, version_main=120)
            
            # Aplicar selenium-stealth para ocultar más rastros
            stealth(self.driver,
                languages=["es-ES", "es", "en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                webdriver=False  # Importante: esconder webdriver
            )
            
            logger.info("✅ Undetected ChromeDriver inicializado exitosamente con stealth")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Undetected ChromeDriver: {str(e)}")
            return False
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"🚀 Iniciando scraping de {self.source_name}")
        
        # ESTRATEGIA 1: Intentar con undetected-chromedriver (MÁS EFECTIVO)
        if UNDETECTED_CHROMEDRIVER_AVAILABLE and Config.USE_SELENIUM:
            try:
                logger.info("📱 Intentando con Undetected ChromeDriver...")
                if self._setup_undetected_chrome():
                    offers = self._scrape_with_undetected()
                    self._cleanup_selenium()
                    
                    if offers and len(offers) > 0:
                        logger.info(f"✅ EXITOSO: {len(offers)} ofertas obtenidas con Undetected ChromeDriver")
                        return offers
                    else:
                        logger.warning("⚠️ Undetected ChromeDriver no obtuvo resultados, probando método HTTP...")
            except Exception as e:
                logger.error(f"❌ Error con Undetected ChromeDriver: {str(e)[:150]}")
                if self.driver:
                    self._cleanup_selenium()
        
        # ESTRATEGIA 2: Fallback a método HTTP mejorado con retry
        try:
            logger.info("🌐 Probando método HTTP con proxies y retry...")
            offers = self._scrape_with_http()
            
            if offers and len(offers) > 0:
                logger.info(f"✅ EXITOSO: {len(offers)} ofertas obtenidas con método HTTP")
                return offers
            else:
                logger.warning("⚠️ Método HTTP no obtuvo resultados")
        except Exception as e:
            logger.error(f"❌ Error con método HTTP: {str(e)[:150]}")
        
        # Último intento: método básico sin mejoras
        try:
            logger.info("🔄 Último intento con método básico...")
            offers = self._scrape_basic()
            
            if offers:
                logger.info(f"✅ EXITOSO: {len(offers)} ofertas obtenidas con método básico")
                return offers
        except Exception as e:
            logger.error(f"❌ Error en método básico: {str(e)[:100]}")
        
        logger.error(f"❌ FALLO TOTAL: No se pudieron obtener ofertas de {self.source_name}")
        return []
        
        # Try multiple URL strategies
        urls_to_try = [
            "https://www.revolico.com/empleos",
            "https://www.revolico.com/empleos",
        ]
        
        # Probar cada URL con método mejorado
        for url in urls_to_try:
            logger.info(f"🔗 Probando URL: {url}")
            
            try:
                response = self._make_request(url)
                
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    offers = self._parse_offers(soup)
                    
                    if offers:
                        return offers
                
                # Esperar entre intentos
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.debug(f"Error con URL {url}: {str(e)[:80]}")
                continue
        
        return []
    
    def _strategy_basic(self, url: str):
        """Basic request with random headers"""
        headers = {
            'User-Agent': random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        return self.session.get(url, headers=headers, timeout=30)
    
    def _strategy_with_referer(self, url: str):
        """Request with Google referer to appear as organic traffic"""
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/',
            'Origin': 'https://www.revolico.com',
        }
        
        return self.session.get(url, headers=headers, timeout=30)
    
    def _strategy_with_cookies(self, url: str):
        """Request with session cookies"""
        # Set some common cookies that real browsers would have
        self.session.cookies.set('language', 'es', domain='.revolico.com')
        self.session.cookies.set('currency', 'CUP', domain='.revolico.com')
        
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Cache-Control': 'no-cache',
        }
        
        return self.session.get(url, headers=headers, timeout=30)
    
    def _strategy_slow_requests(self, url: str):
        """Very slow request to mimic human behavior"""
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
        
        # Add random delay before request
        time.sleep(random.uniform(5, 10))
        
        response = self.session.get(url, headers=headers, timeout=45)
        
        # Add delay after response
        time.sleep(random.uniform(2, 5))
        
        return response
    
    def _cleanup_selenium(self):
        """Clean up Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        offers = []
        
        # Multiple strategies to find job listings
        selectors = [
            'li.listing-item',
            'div.ad-item',
            'article',
            'div.listing',
            '.result-item',
            '.ad-listing',
            'div[class*="item"]',
            'li[class*="listing"]',
            '.post-item',
            '.job-item'
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
                if any(keyword in text for keyword in ['empleo', 'trabajo', 'job', 'oferta', 'contrat']):
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
            
            # Strategy 1: Look for anchor tags
            link_elem = job_element.find('a')
            if link_elem:
                title_elem = link_elem
                link = link_elem.get('href', '')
            else:
                # Strategy 2: Look for headings
                for tag in ['h1', 'h2', 'h3', 'h4']:
                    title_elem = job_element.find(tag)
                    if title_elem:
                        break
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Handle relative URLs
            if link and not link.startswith('http'):
                if link.startswith('/'):
                    link = f"https://www.revolico.com{link}"
                else:
                    link = f"https://www.revolico.com/{link}"
            
            # Extract description
            desc_selectors = [
                'p.description',
                '.description',
                'p',
                '.content',
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
                # Fallback: get first paragraph or text content
                text_parts = job_element.get_text().split('\n')
                description = ' '.join([part.strip() for part in text_parts if part.strip()])[:200]
            
            # Extract company
            company_selectors = [
                '.company',
                '.empresa',
                '.organization',
                '[class*="company"]',
                '[class*="empresa"]'
            ]
            
            company = ''
            for selector in company_selectors:
                company_elem = job_element.select_one(selector)
                if company_elem:
                    company = company_elem.get_text(strip=True)
                    break
            
            if not company:
                # Try to find company in title or description
                title_words = title.split()
                if len(title_words) > 2:
                    potential_company = ' '.join(title_words[:2])
                    if potential_company not in ['Ofertas de', 'Trabajos en']:
                        company = potential_company
            
            if title and link:
                return self._create_offer(title, company, description, link)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting job info: {str(e)}")
            return None
