from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
import requests
from fake_useragent import UserAgent
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseScraper(ABC):
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent()
        self.session = self._create_session()
        logger.info(f"Initialized {source_name} scraper")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        proxies = Config.get_proxies()
        if proxies:
            session.proxies.update(proxies)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def _make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        if retries is None:
            retries = Config.MAX_RETRIES
        
        for attempt in range(retries):
            try:
                logger.debug(f"Attempting request to {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=Config.REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully fetched {url}")
                    return response
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}")
                    time.sleep(Config.REQUEST_DELAY * 2)
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429) for {url}")
                    time.sleep(Config.REQUEST_DELAY * 3)
                else:
                    logger.warning(f"Received status code {response.status_code} for {url}")
                
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
