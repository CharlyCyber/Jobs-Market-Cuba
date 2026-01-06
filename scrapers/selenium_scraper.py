from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from bot.config import Config
from bot.utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class SeleniumBaseScraper(ABC):
    """
    Base scraper usando Selenium para páginas con protección anti-bot
    """
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.driver = None
        self.wait = None
        logger.info(f"Initialized Selenium-based {source_name} scraper")
    
    def _setup_driver(self):
        """Configurar Chrome/Firefox con opciones anti-detection"""
        try:
            chrome_options = Options()
            
            # Opciones básicas de headless
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Opciones para evitar detección
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')  # Más rápido
            chrome_options.add_argument('--disable-javascript')  # Opcional, depende del site
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Opciones adicionales de privacidad
            chrome_options.add_argument('--incognito')
            chrome_options.add_argument('--disable-plugins-discovery')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Configurar prefs
            prefs = {
                "profile.default_content_setting_values": {
                    "cookies": 2,
                    "images": 2,
                    "plugins": 2,
                    "popups": 2,
                    "geolocation": 2,
                    "notifications": 2,
                    "media_stream": 2,
                    "media_stream_mic": 2,
                    "media_stream_camera": 2,
                    "protocol_handlers": 2,
                    "ppapi_broker": 2,
                    "automatic_downloads": 2,
                    "midi_sysex": 2,
                    "push_messaging": 2,
                    "ssl_cert_decisions": 2,
                    "metro_switch_to_desktop": 2,
                    "protected_media_identifier": 2,
                    "app_banner": 2,
                    "site_engagement": 2,
                    "durable_storage": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Inicializar driver
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Ejecutar script para ocultar Selenium
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']})")
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Selenium driver initialized successfully")
            
        except WebDriverException as e:
            logger.error(f"Failed to initialize Selenium driver: {str(e)}")
            raise
    
    def _human_like_scroll(self):
        """Simular scroll humano"""
        scroll_pause = random.uniform(0.5, 2.0)
        
        # Scroll aleatorio
        for _ in range(random.randint(2, 5)):
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 1.0))
        
        time.sleep(scroll_pause)
    
    def _human_like_typing(self, element, text: str):
        """Simular tipeo humano"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.3))
    
    def _wait_for_element(self, by: By, value: str, timeout: int = 10, condition: str = 'presence'):
        """Esperar elemento con diferentes condiciones"""
        try:
            if condition == 'presence':
                return self.wait.until(EC.presence_of_element_located((by, value)))
            elif condition == 'visible':
                return self.wait.until(EC.visibility_of_element_located((by, value)))
            elif condition == 'clickable':
                return self.wait.until(EC.element_to_be_clickable((by, value)))
        except TimeoutException:
            logger.warning(f"Timeout waiting for element {by}={value}")
            return None
    
    def _make_request_selenium(self, url: str) -> bool:
        """Navegar a URL usando Selenium"""
        try:
            logger.info(f"Navigating to {url} with Selenium")
            
            # Navegar con delay
            time.sleep(random.uniform(1, 2))
            self.driver.get(url)
            
            # Esperar que cargue
            time.sleep(random.uniform(2, 4))
            
            # Scroll humano
            self._human_like_scroll()
            
            logger.info(f"Successfully loaded {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False
    
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
    
    def cleanup(self):
        """Cerrar driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium driver closed successfully")
            except:
                pass
