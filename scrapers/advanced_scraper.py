from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
import httpx
from fake_useragent import UserAgent
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class AdvancedBaseScraper(ABC):
    """
    Scraper base avanzado usando httpx con técnicas anti-detection
    """
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.ua = UserAgent()
        self.client = self._create_client()
        logger.info(f"Initialized advanced {source_name} scraper")
    
    def _create_client(self) -> httpx.Client:
        """Crear cliente httpx con configuración anti-detection"""
        # Configurar límites de conexión
        limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0
        )
        
        # Configurar transport con HTTP/2
        transport = httpx.HTTPTransport(
            http2=True,
            verify=True,
            limits=limits
        )
        
        client = httpx.Client(
            transport=transport,
            timeout=httpx.Timeout(Config.REQUEST_TIMEOUT, connect=10.0),
            follow_redirects=True,
            http2=True
        )
        
        return client
    
    def _get_headers(self) -> Dict[str, str]:
        """Generar headers ultra realistas"""
        user_agent = self.ua.random
        
        # Headers que simulan navegador al 99%
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7,es-CU;q=0.6',
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
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        return headers
    
    def _make_request(self, url: str, method: str = 'GET', data: Optional[Dict] = None, retries: int = None) -> Optional[httpx.Response]:
        """Realizar request con técnicas anti-detection"""
        if retries is None:
            retries = Config.MAX_RETRIES
        
        for attempt in range(retries):
            try:
                logger.debug(f"Attempting {method} request to {url} (attempt {attempt + 1}/{retries})")
                
                # Human-like delay
                delay = Config.REQUEST_DELAY + random.uniform(1, 3)
                logger.debug(f"Waiting {delay:.2f}s before request...")
                time.sleep(delay)
                
                if method.upper() == 'GET':
                    response = self.client.get(
                        url,
                        headers=self._get_headers(),
                        follow_redirects=True
                    )
                else:  # POST
                    response = self.client.post(
                        url,
                        headers=self._get_headers(),
                        data=data,
                        follow_redirects=True
                    )
                
                # Verificar response
                if response.status_code == 200:
                    # Validar que no es página de bloqueo
                    if self._is_blocked_page(response.text):
                        logger.warning(f"Detected blocking page for {url}")
                        time.sleep(Config.REQUEST_DELAY * 3)
                        continue
                    
                    logger.info(f"Successfully fetched {url}")
                    time.sleep(random.uniform(0.5, 1.5))
                    return response
                
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden (403) for {url}")
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
                
            except httpx.TimeoutException:
                logger.error(f"Timeout while fetching {url}")
            except httpx.RequestError as e:
                logger.error(f"Request error for {url}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {str(e)}")
            
            if attempt < retries - 1:
                delay = Config.REQUEST_DELAY + random.uniform(0, 2)
                logger.debug(f"Waiting {delay:.2f}s before retry...")
                time.sleep(delay)
        
        logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None
    
    def _is_blocked_page(self, html: str) -> bool:
        """Detectar si la página es una página de bloqueo/captcha"""
        blocked_indicators = [
            'captcha',
            'cloudflare',
            'access denied',
            'forbidden',
            'ddos protection',
            'incapsula',
            'sucuri',
            'blocked',
            'security check',
        ]
        
        html_lower = html.lower()
        for indicator in blocked_indicators:
            if indicator in html_lower:
                logger.warning(f"Blocking indicator detected: {indicator}")
                return True
        
        return False
    
    def _rotate_user_agent(self):
        """Rotar user agent"""
        self.ua = UserAgent()
        logger.debug(f"Rotated to new User-Agent: {self.ua.random}")
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, str]]:
        pass
    
    def _create_offer(self, title: str, company: str, description: str, link: str) -> Dict[str, str]:
        return {
            'title': title.strip(),
            'company': company.strip() if company else 'No especificada',
            'description': description.strip(),
            'link': link.strip(),
            'source': self.source_name
        }
