from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
import requests
from fake_useragent import UserAgent
import json
import hashlib
import base64
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseScraper(ABC):
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent()
        self.session = self._create_session()
        self.request_count = 0
        self.session_id = hashlib.md5(f"{source_name}_{time.time()}".encode()).hexdigest()[:8]
        logger.info(f"Initialized {source_name} scraper with session ID: {self.session_id}")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        # Enhanced anti-detection session settings
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0,  # We handle retries manually
            pool_block=False
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Set up cookie jar for session persistence
        session.cookies.clear()
        
        proxies = Config.get_proxies()
        if proxies:
            session.proxies.update(proxies)
        
        # Fix encoding issues - don't force identity encoding
        # Let requests handle encoding automatically
        
        # Add random delays between requests
        session.delay_range = (2, 5)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        # Enhanced headers to avoid detection
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
        ]
        
        # Rotate platform info based on user agent
        ua = random.choice(user_agents)
        platform = "Windows"
        if "Macintosh" in ua:
            platform = "macOS"
        elif "Linux" in ua:
            platform = "Linux"
        
        return {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': f'"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': f'"{platform}"',
        }
    
    def _make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        if retries is None:
            retries = Config.MAX_RETRIES
        
        self.request_count += 1
        logger.debug(f"Request #{self.request_count} to {url} (attempt 1/{retries})")
        
        # Add random delay between requests to mimic human behavior
        if self.request_count > 1:
            delay = random.uniform(*self.session.delay_range)
            logger.debug(f"Waiting {delay:.2f}s before request...")
            time.sleep(delay)
        
        for attempt in range(retries):
            try:
                logger.debug(f"Attempting request to {url} (attempt {attempt + 1}/{retries})")
                
                headers = self._get_headers()
                
                # Add session-specific headers
                headers.update({
                    'X-Requested-With': 'XMLHttpRequest',  # Common AJAX header
                    'X-Session-ID': self.session_id,
                })
                
                # For Revolico, add extra headers to avoid detection
                if 'revolico.com' in url.lower():
                    headers.update({
                        'Referer': 'https://www.google.com/',
                        'Origin': 'https://www.revolico.com',
                    })
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=Config.REQUEST_TIMEOUT,
                    allow_redirects=True,
                    stream=False  # Get full response immediately
                )
                
                if response.status_code == 200:
                    # Fix encoding issues
                    try:
                        response.encoding = 'utf-8'
                        # Ensure the content is properly decoded
                        if response.content:
                            response.text
                    except UnicodeDecodeError:
                        logger.warning(f"Encoding issues with {url}, trying different encoding")
                        response.encoding = 'iso-8859-1'
                    
                    logger.info(f"Successfully fetched {url}")
                    return response
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}")
                    if attempt < retries - 1:
                        # Wait longer for 403 errors
                        time.sleep(Config.REQUEST_DELAY * (attempt + 2))
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429) for {url}")
                    if attempt < retries - 1:
                        # Wait much longer for rate limits
                        time.sleep(Config.REQUEST_DELAY * (attempt + 5))
                elif response.status_code == 404:
                    logger.warning(f"Page not found (404) for {url}")
                    break  # Don't retry 404 errors
                else:
                    logger.warning(f"Received status code {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(Config.REQUEST_DELAY * (attempt + 1))
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout while fetching {url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {str(e)}")
            
            if attempt < retries - 1:
                delay = Config.REQUEST_DELAY + random.uniform(0, 2)
                logger.debug(f"Waiting {delay:.2f}s before retry...")
                time.sleep(delay)
        
        logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, str]]:
        pass
    
    def _create_offer(
        self,
        title: str,
        company: str,
        description: str,
        link: str
    ) -> Dict[str, str]:
        return {
            'title': title.strip(),
            'company': company.strip() if company else 'No especificada',
            'description': description.strip(),
            'link': link.strip(),
            'source': self.source_name
        }
