from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.advanced_scraper import AdvancedBaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger
import re
from urllib.parse import urljoin, urlparse

logger = setup_logger(__name__)


class FallbackRevolicoScraper(AdvancedBaseScraper):
    """
    Scraper para Revolico usando múltiples estrategias de fallback
    cuando la protección anti-bot es demasiado fuerte
    """
    
    def __init__(self):
        super().__init__("Revolico-Fallback")
        
        # URLs alternativas para intentar
        self.alt_urls = [
            "https://www.revolico.com/empleos/",
            "https://revolico.com/search?category=empleos&subcategory=ofertas-de-empleo",
            "https://www.revolico.com/search/empleos",
        ]
        
        # Si la búsqueda principal falla, usar URLs directas de categorías
        self.direct_category_urls = [
            "https://www.revolico.com/computadoras-y-accesorios/empleos/",
            "https://www.revolico.com/empleos/",
            "https://www.revolico.com/servicios/empleos/",
        ]
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting FALLBACK scraping for {self.source_name}")
        
        offers = []
        
        # Estrategia 1: Intentar URLs alternativas
        for url in self.alt_urls:
            logger.info(f"Trying alternative URL: {url}")
            response = self._make_request(url)
            
            if response and len(response.text) > 2000:  # HTML válido
                logger.info(f"✓ Successfully accessed: {url}")
                offers = self._parse_offers_from_html(response.text, url)
                if offers:
                    break
        
        # Estrategia 2: Si fallan las URLs alternativas, buscar páginas directas
        if not offers:
            logger.info("Strategy 1 failed, trying direct category access...")
            for url in self.direct_category_urls:
                logger.info(f"Trying direct category: {url}")
                response = self._make_request(url)
                
                if response and len(response.text) > 2000:
                    logger.info(f"✓ Successfully accessed category: {url}")
                    offers = self._parse_offers_from_html(response.text, url)
                    if offers:
                        break
        
        # Estrategia 3: Crawling interno - buscar links de ofertas en la página principal
        if not offers:
            logger.info("Strategy 2 failed, attempting internal crawling...")
            offers = self._crawl_internal_links()
        
        logger.info(f"Fallback scraping found {len(offers)} offers")
        return offers
    
    def _parse_offers_from_html(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Parsear ofertas usando múltiples estrategias"""
        offers = []
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Método 1: Selectores específicos
            offers = self._parse_with_selectors(soup, base_url)
            
            # Método 2: Si fallan selectores específicos, usar genérico
            if not offers:
                offers = self._parse_generic(soup, base_url)
            
            # Método 3: Regex fallback
            if not offers:
                offers = self._parse_regex(html, base_url)
        
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            # Fallback total a regex
            offers = self._parse_regex(html, base_url)
        
        return offers
    
    def _parse_with_selectors(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Parsear usando selectores CSS específicos"""
        offers = []
        
        # Lista de selectores que funcionan en diferentes versiones de Revolico
        selectors = [
            ('li.listing-item', 'a.listing-title', 'p.description'),
            ('div.ad-item', 'h2 a', 'p'),
            ('article', 'h3 a', 'div.description'),
            ('div[data-item]', 'a[data-title]', 'div.text'),
        ]
        
        for container_sel, title_sel, desc_sel in selectors:
            containers = soup.select(container_sel)
            
            for container in containers:
                try:
                    title_elem = container.select_one(title_sel)
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    
                    # Validar que sea una oferta de empleo
                    if not self._is_valid_job(title, href):
                        continue
                    
                    link = urljoin(base_url, href)
                    
                    # Extraer descripción
                    desc_elem = container.select_one(desc_sel) if desc_sel else None
                    description = desc_elem.get_text(strip=True) if desc_elem else "Ver descripción en el enlace"
                    
                    # Intentar encontrar empresa
                    company = self._extract_company(container)
                    
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
                
                except Exception as e:
                    logger.debug(f"Error parsing container: {str(e)}")
                    continue
            
            if offers:
                logger.info(f"Found {len(offers)} offers with selector {container_sel}")
                break
        
        return offers
    
    def _parse_generic(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Parsear genérico: encontrar todos los links posibles"""
        offers = []
        
        # Encontrar todos los links que parezcan ofertas
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # Validar link
            if not self._is_valid_job(title, href):
                continue
            
            link_url = urljoin(base_url, href)
            
            # Buscar contexto (descripción cercana)
            description = self._find_description_nearby(link)
            
            offer = self._create_offer(title, "", description, link_url)
            offers.append(offer)
        
        logger.info(f"Generic parsing found {len(offers)} potential job links")
        return offers
    
    def _parse_regex(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """Fallback final: parsing con regex"""
        offers = []
        
        # Pattern para encontrar links con títulos de ofertas de trabajo
        patterns = [
            r'<a[^>]+href=["\']([^"\']*empleo[^"\']*)["\'][^>]*>([^<]{10,100})</a>',
            r'<a[^>]+href=["\']([^"\']*trabajo[^"\']*)["\'][^>]*>([^<]{10,100})</a>',
            r'<a[^>]+href=["\']([^"\']*oferta[^"\']*)["\'][^>]*>([^<]{10,100})</a>',
            r'<a[^>]+href=["\']([^"\']*vacante[^"\']*)["\'][^>]*>([^<]{10,100})</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.MULTILINE)
            
            for href, title in matches[:15]:  # Limitar para evitar spam
                if self._is_valid_job(title, href):
                    link = urljoin(base_url, href)
                    offer = self._create_offer(title, "", "Ver descripción en el enlace", link)
                    offers.append(offer)
        
        logger.info(f"Regex parsing found {len(offers)} offers")
        return offers
    
    def _is_valid_job(self, title: str, href: str) -> bool:
        """Validar si un link/título parece ser una oferta de empleo"""
        # Debe tener título
        if not title or len(title) < 5:
            return False
        
        # Debe tener link válido
        if not href or href.startswith(('#', 'javascript:', 'mailto:')):
            return False
        
        # Palabras clave que indican empleo
        job_keywords = [
            'empleo', 'trabajo', 'oferta', 'vacante', 'puesto', 'cargo',
            'position', 'job', 'hiring', 'work', 'opportunity'
        ]
        
        text_combined = (title + ' ' + href).lower()
        
        for keyword in job_keywords:
            if keyword in text_combined:
                return True
        
        return False
    
    def _extract_company(self, container) -> str:
        """Extraer nombre de empresa del container"""
        company_selectors = ['.company', '.advertiser', '.empresa', '.business', 'span.meta']
        
        for selector in company_selectors:
            elem = container.select_one(selector)
            if elem:
                company = elem.get_text(strip=True)
                if len(company) < 50:
                    return company
        
        return ""
    
    def _find_description_nearby(self, element) -> str:
        """Buscar descripción cerca del elemento"""
        # Buscar hermanos siguientes
        for sibling in element.find_all_next(['p', 'div'], limit=2):
            text = sibling.get_text(strip=True)
            if 20 < len(text) < 300:
                return text
        
        return "Ver descripción en el enlace"
    
    def _crawl_internal_links(self) -> List[Dict[str, str]]:
        """Estrategia 3: Navegar a links internos para encontrar ofertas"""
        offers = []
        
        try:
            # Primero obtener la página principal
            response = self._make_request("https://www.revolico.com")
            
            if not response:
                return offers
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Encontrar sección de empleos y sus links
            job_section_links = []
            
            # Buscar links que contengan 'empleo', 'trabajo', 'empleos', 'jobs'
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in ['empleo', 'trabajo', 'job']):
                    full_url = urljoin("https://www.revolico.com", link.get('href'))
                    job_section_links.append(full_url)
            
            # Intentar navegar a cada sección de empleos encontrada
            for job_url in list(set(job_section_links))[:5]:  # Probar las primeras 5 únicas
                logger.info(f"Crawling job section: {job_url}")
                
                response = self._make_request(job_url)
                if response and len(response.text) > 2000:
                    section_offers = self._parse_offers_from_html(response.text, job_url)
                    offers.extend(section_offers)
        
        except Exception as e:
            logger.error(f"Error in internal crawling: {str(e)}")
        
        return offers
