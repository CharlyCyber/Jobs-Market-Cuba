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
        logger.info(f"Initialized {source_name} scraper with advanced anti-detection")
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        
        proxies = Config.get_proxies()
        if proxies:
            session.proxies.update(proxies)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        # Generar headers que simulen un navegador real con más detalles
        user_agent = self.ua.random
        
        # Headers adicionales para simular navegador real
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'es-ES,es-CU;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate', 
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.google.com/',
        }
        
        # Para Chrome-like UAs, añadir headers específicos
        if 'Chrome' in user_agent or 'Chromium' in user_agent:
            headers['sec-ch-ua'] = '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"'
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = '"Windows"'
        
        return headers
    
    def _make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        if retries is None:
            retries = Config.MAX_RETRIES
        
        for attempt in range(retries):
            try:
                logger.debug(f"Attempting request to {url} (attempt {attempt + 1}/{retries})")
                
                # Simular delay humano con variabilidad
                delay = Config.REQUEST_DELAY + random.uniform(1, 3)
                logger.debug(f"Waiting {delay:.2f}s before request...")
                time.sleep(delay)
                
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    timeout=Config.REQUEST_TIMEOUT,
                    allow_redirects=True,
                    verify=True  # Verificar SSL
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully fetched {url}")
                    # Simular lectura de página real
                    time.sleep(random.uniform(0.5, 1.5))
                    return response
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}")
                    # Incrementar delay exponencial
                    wait_time = Config.REQUEST_DELAY * (2 ** attempt)
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429) for {url}")
                    time.sleep(Config.REQUEST_DELAY * 3)
                elif response.status_code == 503:
                    logger.warning(f"Service unavailable (503) for {url}")
                    time.sleep(Config.REQUEST_DELAY * 2)
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
