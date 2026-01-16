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
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from scrapers.proxy_rotator import ProxyRotator
from scrapers.cache import CacheManager
from scrapers.metrics import ScrapingMetrics

logger = setup_logger(__name__)


class BaseScraper(ABC):
    
    def __init__(self, source_name: str, use_cache: bool = True, use_proxy: bool = True):
        self.source_name = source_name
        self.ua = UserAgent()
        self.session = self._create_session()
        self.request_count = 0
        self.session_id = hashlib.md5(f"{source_name}_{time.time()}".encode()).hexdigest()[:8]
        
        # Nuevos componentes: proxy rotator, cache y métricas
        self.use_cache = use_cache
        self.use_proxy = use_proxy
        
        if use_proxy:
            self.proxy_rotator = ProxyRotator()
        else:
            self.proxy_rotator = None
        
        if use_cache:
            self.cache = CacheManager()
        else:
            self.cache = None
        
        self.metrics = ScrapingMetrics()
        
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
        
        # Add random delays between requests (AUMENTADO para más seguridad)
        session.delay_range = (5, 10)  # Aumentado de (2, 5) a (5, 10)
        
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
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Método mejorado de request con cache, proxy y retry automático"""
        
        self.request_count += 1
        start_time = time.time()
        
        # CHECK 1: Verificar cache primero
        if self.cache:
            cached_data = self.cache.get(url)
            if cached_data:
                # Retornar un objeto Response simulado con datos cacheados
                self.metrics.record_cache_hit()
                logger.info(f"✓ Cache HIT para {url[:60]}...")
                
                # Crear response simulado
                class CachedResponse:
                    def __init__(self, content):
                        self.content = content
                        self.status_code = 200
                        self.text = content.decode('utf-8', errors='ignore')
                        self.encoding = 'utf-8'
                
                return CachedResponse(cached_data.get('content', b''))
        
        # CHECK 2: Verificar si usamos proxy
        proxy = None
        if self.use_proxy and self.proxy_rotator:
            proxy = self.proxy_rotator.get_next_proxy()
        
        logger.info(f"🌐 Request #{self.request_count} a {url[:60]}...")
        if proxy:
            logger.debug(f"   Proxy: {proxy.get('http', 'sin proxy')[:30]}...")
        
        # Retry con Tenacity (exponential backoff)
        @retry(
            stop=stop_after_attempt(Config.MAX_RETRIES),
            wait=wait_exponential(multiplier=1, min=5, max=30),
            retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
            before_sleep=lambda retry_state: logger.info(f"🔄 Reintento #{retry_state.attempt_number} esperando {retry_state.next_action:.1f}s...")
        )
        def _do_request():
            # Obtener proxy actual
            current_proxy = None
            if self.use_proxy and self.proxy_rotator:
                current_proxy = self.proxy_rotator.get_next_proxy()
            
            # Headers mejorados
            headers = self._get_headers()
            
            # Headers adicionales
            headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'X-Session-ID': self.session_id,
            })
            
            # Headers específicos para Revolico
            if 'revolico.com' in url.lower():
                headers.update({
                    'Referer': 'https://www.google.com/',
                    'Origin': 'https://www.revolico.com',
                })
            
            # Hacer request
            response = self.session.get(
                url,
                headers=headers,
                proxies=current_proxy,
                timeout=Config.REQUEST_TIMEOUT,
                allow_redirects=True,
                stream=False
            )
            
            # Validar respuesta
            if response.status_code == 200:
                # Guardar en cache
                if self.cache and response.content:
                    try:
                        self.cache.set(url, {'content': response.content.hex()})
                        logger.debug(f"✓ Cache guardado para {url[:50]}...")
                    except:
                        pass
                
                # Marcar proxy como exitoso
                if current_proxy and self.use_proxy:
                    proxy_url = current_proxy.get('http', '')
                    self.proxy_rotator.mark_success(proxy_url)
                
                return response
            
            elif response.status_code in [403, 429]:
                # Marcar proxy como fallido
                if current_proxy and self.use_proxy:
                    proxy_url = current_proxy.get('http', '')
                    self.proxy_rotator.mark_failed(proxy_url)
                    self.metrics.record_proxy_failure()
                
                # Lanzar excepción para que tenacity reintente
                error_msg = f"Error {response.status_code} - {url}"
                if response.status_code == 403:
                    logger.warning(f"🚫 ACCESO DENEGADO (403)")
                else:
                    logger.warning(f"🚫 RATE LIMIT (429)")
                
                raise requests.exceptions.HTTPError(error_msg)
            
            elif response.status_code == 404:
                logger.warning(f"❌ PÁGINA NO ENCONTRADA (404) - {url}")
                raise requests.exceptions.HTTPError("Page not found")
            
            else:
                logger.warning(f"⚠️ Status code: {response.status_code} - {url}")
                raise requests.exceptions.HTTPError(f"Unexpected status: {response.status_code}")
        
        try:
            response = _do_request()
            
            # Registrar métricas de éxito
            elapsed_time = time.time() - start_time
            self.metrics.record_success(elapsed_time)
            
            logger.info(f"✅ ÉXITO - {url[:50]}... ({elapsed_time:.2f}s)")
            return response
            
        except Exception as e:
            # Registrar métricas de fallo
            self.metrics.record_failure(str(e)[:100])
            logger.error(f"❌ FALLO - {url[:50]}... | {str(e)[:100]}")
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
