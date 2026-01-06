from typing import List, Dict
from bs4 import BeautifulSoup
from scrapers.advanced_scraper import AdvancedBaseScraper
from bot.config import Config
from bot.utils.logger import setup_logger
import re

logger = setup_logger(__name__)


class RevolicoEnhancedScraper(AdvancedBaseScraper):
    
    def __init__(self):
        super().__init__("Revolico")
        self.url = Config.REVOLICO_URL
    
    def scrape(self) -> List[Dict[str, str]]:
        logger.info(f"Starting ENHANCED scraping from {self.source_name}")
        
        offers = []
        
        # Hacer request con técnicas anti-detection
        response = self._make_request(self.url)
        if not response:
            logger.error(f"Failed to fetch data from {self.source_name} with enhanced methods")
            return []
        
        try:
            # Verificar si es HTML válido
            if len(response.text) < 1000:
                logger.warning(f"Response too short ({len(response.text)} chars), might be blocked")
                return []
            
            soup = BeautifulSoup(response.content, 'lxml')  # Usar lxml parser más rápido
            
            # Intentar detectar si hay JavaScript que genere el contenido
            if self._has_js_generated_content(soup):
                logger.info("Detected JS-generated content, attempting fallback parsing")
            
            offers = self._parse_offers(soup)
            logger.info(f"Successfully scraped {len(offers)} offers from {self.source_name}")
            
        except Exception as e:
            logger.error(f"Error parsing {self.source_name} with enhanced methods: {str(e)}")
            # Intentar análisis básico del HTML como fallback
            offers = self._emergency_parse(response.text)
        
        return offers
    
    def _has_js_generated_content(self, soup: BeautifulSoup) -> bool:
        """Detectar si el contenido está generado por JS"""
        # Buscar elementos que sugieren carga dinámica
        scripts = soup.find_all('script')
        noscript = soup.find_all('noscript')
        
        # Si hay muchos scripts y poco contenido en el body, probablemente es JS-heavy
        body_content = soup.find('body')
        if body_content:
            text_length = len(body_content.get_text(strip=True))
            script_count = len(scripts)
            
            if script_count > 10 and text_length < 500:
                logger.info(f"JS-heavy page detected: {script_count} scripts, {text_length} chars body")
                return True
        
        return False
    
    def _parse_offers(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Parsear ofertas usando múltiples estrategias"""
        offers = []
        
        # Varios patrones de selectores para encontrar listings
        selector_patterns = [
            # Patrón 1: Listings con clases específicas
            {'selector': ('li', 'listing-item'), 'title': ('a', 'listing-title'), 'desc': ('p', 'description')},
            # Patrón 2: Anuncios genéricos
            {'selector': ('div', 'ad-item'), 'title': ('h2', None), 'desc': ('p', None)},
            # Patrón 3: Artículos de ofertas
            {'selector': ('article', 'job-item'), 'title': ('a', None), 'desc': ('div', 'description')},
            # Patrón 4: Cards de trabajo
            {'selector': ('div', 'job-card'), 'title': ('h3', None), 'desc': ('p', 'summary')},
        ]
        
        for pattern in selector_patterns:
            listings = self._find_listings(soup, pattern['selector'])
            if listings:
                logger.info(f"Found {len(listings)} listings with pattern: {pattern['selector']}")
                parsed_offers = self._extract_from_listings(listings, pattern)
                offers.extend(parsed_offers)
        
        # Si no encontramos nada con selectores específicos, intentar parsing genérico
        if not offers:
            logger.warning("No offers found with specific patterns, attempting generic parsing")
            offers = self._generic_parse(soup)
        
        return offers
    
    def _find_listings(self, soup: BeautifulSoup, selector: tuple) -> List:
        """Encontrar listings con un selector específico"""
        tag, class_name = selector
        if class_name:
            return soup.find_all(tag, class_=class_name)
        else:
            return soup.find_all(tag)
    
    def _extract_from_listings(self, listings: List, pattern: Dict) -> List[Dict[str, str]]:
        """Extraer información de listings usando un patrón"""
        offers = []
        
        for listing in listings:
            try:
                # Extraer título y link
                title_tag, title_class = pattern['title']
                if title_class:
                    title_elem = listing.find(title_tag, class_=title_class)
                else:
                    title_elem = listing.find(title_tag)
                
                if not title_elem:
                    # Buscar cualquier link dentro del listing
                    link_elem = listing.find('a')
                    if link_elem:
                        title_elem = link_elem
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                if not link:
                    # Buscar link en el listing
                    link_elem = listing.find('a')
                    if link_elem:
                        link = link_elem.get('href', '')
                
                if link:
                    link = self._normalize_link(link)
                
                # Extraer descripción
                desc_tag, desc_class = pattern['desc']
                description = "Descripción no disponible"
                if desc_class:
                    desc_elem = listing.find(desc_tag, class_=desc_class)
                else:
                    desc_elem = listing.find(desc_tag)
                
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Buscar empresa si está disponible
                company = self._find_company(listing)
                
                if title and link:
                    offer = self._create_offer(title, company, description, link)
                    offers.append(offer)
            
            except Exception as e:
                logger.debug(f"Error parsing listing: {str(e)}")
                continue
        
        return offers
    
    def _normalize_link(self, link: str) -> str:
        """Normalizar link a URL completa"""
        if link.startswith('http'):
            return link
        elif link.startswith('/'):
            return f"https://www.revolico.com{link}"
        else:
            return f"https://www.revolico.com/{link}"
    
    def _find_company(self, listing) -> str:
        """Intentar encontrar el nombre de la empresa"""
        company_selectors = [
            ('span', 'company'),
            ('div', 'company'),
            ('span', 'advertiser'),
            ('div', 'advertiser'),
            ('div', 'metadata'),
        ]
        
        for tag, class_name in company_selectors:
            if class_name:
                elem = listing.find(tag, class_=class_name)
            else:
                elem = listing.find(tag)
            
            if elem:
                company = elem.get_text(strip=True)
                # Evitar textos muy largos (probablemente no sean empresa)
                if len(company) < 50 and company:
                    return company
        
        return ""
    
    def _generic_parse(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Parsing genérico cuando no funcionan los selectores específicos"""
        offers = []
        
        # Buscar todos los links que puedan ser ofertas
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            try:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filtrar links de ofertas válidos
                if self._is_job_link(href, text):
                    title = text if text else "Oferta de empleo"
                    link_url = self._normalize_link(href)
                    
                    # Buscar descripción en elementos cercanos
                    description = self._find_nearby_description(link)
                    
                    offer = self._create_offer(title, "", description, link_url)
                    offers.append(offer)
            
            except:
                continue
        
        logger.info(f"Generic parsing found {len(offers)} potential offers")
        return offers
    
    def _is_job_link(self, href: str, text: str) -> bool:
        """Determinar si un link es probablemente una oferta de empleo"""
        # Debe tener href válido
        if not href or href.startswith(('#', 'javascript:', 'mailto:')):
            return False
        
        # Debe tener texto
        if not text or len(text) < 5:
            return False
        
        # Palabras clave que indican empleo
        job_keywords = ['empleo', 'trabajo', 'oferta', 'vacante', 'posición', 'puesto']
        text_lower = text.lower()
        
        for keyword in job_keywords:
            if keyword in text_lower:
                return True
        
        # PATTERNS de URL que indican empleo
        job_patterns = [
            r'empleo',
            r'trabajo',
            r'oferta',
            r'vacante',
            r'puesto',
            r'position',
            r'job',
        ]
        
        href_lower = href.lower()
        for pattern in job_patterns:
            if re.search(pattern, href_lower):
                return True
        
        return False
    
    def _find_nearby_description(self, element) -> str:
        """Buscar descripción cerca del elemento"""
        # Buscar párrafos cercanos
        for sibling in element.find_all_next(['p', 'div'], limit=3):
            text = sibling.get_text(strip=True)
            if len(text) > 20 and len(text) < 500:
                return text
        
        # Buscar párrafos anteriores
        for sibling in element.find_all_previous(['p', 'div'], limit=3):
            text = sibling.get_text(strip=True)
            if len(text) > 20 and len(text) < 500:
                return text
        
        return "Descripción no disponible"
    
    def _emergency_parse(self, html: str) -> List[Dict[str, str]]:
        """Fallback cuando todo lo demás falla - regex scraping"""
        offers = []
        
        # Pattern para encontrar títulos y links
        # Buscar patrones comunes: <a href="...">Título del trabajo</a>
        patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{10,100})</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for href, title in matches[:20]:  # Limitar a 20 resultados
                if self._is_job_link(href, title):
                    link = self._normalize_link(href)
                    offer = self._create_offer(title, "", "Descripción no disponible", link)
                    offers.append(offer)
        
        logger.warning(f"Emergency regex parsing found {len(offers)} offers")
        return offers
