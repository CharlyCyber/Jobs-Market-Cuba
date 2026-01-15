from typing import List, Dict
from bs4 import BeautifulSoup
import time
import random
import json
from scrapers.base_scraper import BaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import Selenium, but make it optional
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available - will use only HTTP requests")


class RevolicoScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("Revolico")
        self.url = Config.REVOLICO_URL
        self.driver = None
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver with advanced anti-detection measures"""
        if not SELENIUM_AVAILABLE:
            return False
            
        chrome_options = Options()
        
        # Advanced anti-detection options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Random user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
        ]
        
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Additional stealth options
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")  # Sometimes helps
        chrome_options.add_argument("--disable-css")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en']})")
            
            logger.info("Selenium WebDriver initialized successfully with stealth mode")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {str(e)}")
            return False
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting scraping from {self.source_name}")
        
        # Try Selenium first for better success rate with anti-bot protection
        if Config.USE_SELENIUM and SELENIUM_AVAILABLE:
            try:
                if self._setup_selenium():
                    offers = self._scrape_with_selenium()
                    self._cleanup_selenium()
                    if offers:
                        logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name} using Selenium")
                        return offers
            except Exception as e:
                logger.error(f"Selenium scraping failed for {self.source_name}: {str(e)}")
                if self.driver:
                    self._cleanup_selenium()
        
        # Try multiple URL strategies
        urls_to_try = [
            "https://www.revolico.com/empleos",
            "https://www.revolico.com/ofertas-de-empleo",
            "https://www.revolico.com/trabajo",
            "https://www.revolico.com/empleos/ofertas-de-empleo",
        ]
        
        for url in urls_to_try:
            logger.info(f"Trying URL: {url}")
            
            # Try with different request patterns
            offers = self._scrape_with_advanced_requests(url)
            if offers:
                logger.info(f"Successfully scraped {len(offers)} offers from {url}")
                return offers
        
        logger.error("All scraping methods failed for Revolico")
        return []
    
    def _scrape_with_selenium(self) -> List[Dict[str, str]]:
        """Scrape using Selenium WebDriver with advanced techniques"""
        try:
            logger.info(f"Loading page with Selenium: {self.url}")
            
            # First, visit a general page to establish session
            self.driver.get("https://www.revolico.com")
            time.sleep(random.uniform(3, 5))
            
            # Then navigate to the jobs page
            self.driver.get(self.url)
            
            # Wait for dynamic content
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Random scrolling to mimic human behavior
            for i in range(3):
                self.driver.execute_script(f"window.scrollTo(0, {(i+1) * document.body.scrollHeight / 4});")
                time.sleep(random.uniform(1, 2))
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            return self._parse_offers(soup)
            
        except Exception as e:
            logger.error(f"Error in Selenium scraping: {str(e)}")
            return []
    
    def _scrape_with_advanced_requests(self, url: str) -> List[Dict[str, str]]:
        """Scrape using advanced HTTP request techniques"""
        
        # Different request strategies to avoid detection
        strategies = [
            self._strategy_basic,
            self._strategy_with_referer,
            self._strategy_with_cookies,
            self._strategy_slow_requests
        ]
        
        for strategy in strategies:
            try:
                logger.debug(f"Trying strategy: {strategy.__name__}")
                response = strategy(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    offers = self._parse_offers(soup)
                    if offers:
                        return offers
                time.sleep(random.uniform(2, 4))  # Delay between strategies
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {str(e)}")
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
