"""
Proxy Rotator - Rotación automática de proxies gratuitos
Este sistema cambia de proxy automáticamente en cada request para evitar bloqueos
"""

import random
import json
from pathlib import Path
from typing import Optional, Dict, List
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProxyRotator:
    
    def __init__(self, proxy_file: str = 'scrapers/proxy_list.txt'):
        self.proxy_file = Path(proxy_file)
        self.proxies: List[Dict[str, str]] = []
        self.failed_proxies = set()
        self.current_index = 0
        
        self._load_proxies()
        logger.info(f"ProxyRotator inicializado con {len(self.proxies)} proxies")
    
    def _load_proxies(self):
        """Carga proxies desde archivo"""
        if not self.proxy_file.exists():
            logger.warning("No se encontró archivo de proxies, usando sin proxy")
            self.proxies = []
            return
        
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                proxy_lines = f.readlines()
                
                for line in proxy_lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Formato: http://user:pass@host:port o http://host:port
                        if '://' in line:
                            proxy = {'http': line, 'https': line}
                            self.proxies.append(proxy)
                            logger.debug(f"Proxy cargado: {line[:20]}...")
            
            logger.info(f"Se cargaron {len(self.proxies)} proxies del archivo")
            
        except Exception as e:
            logger.error(f"Error cargando proxies: {e}")
            self.proxies = []
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Obtiene el siguiente proxy disponible"""
        if not self.proxies:
            logger.debug("No hay proxies configurados")
            return None
        
        # Filtrar proxies que no han fallado
        available = [p for p in self.proxies 
                    if p.get('http', '') not in self.failed_proxies]
        
        if not available:
            # Si todos fallaron, resetear y volver a intentar
            logger.warning("Todos los proxies fallaron, reseteando...")
            self.failed_proxies.clear()
            available = self.proxies
        
        # Seleccionar proxy aleatorio de los disponibles
        proxy = random.choice(available)
        logger.debug(f"Usando proxy: {proxy['http'][:30]}...")
        return proxy
    
    def mark_failed(self, proxy_url: str):
        """Marca un proxy como fallido"""
        self.failed_proxies.add(proxy_url)
        logger.warning(f"Proxy marcado como fallido: {proxy_url[:30]}...")
    
    def mark_success(self, proxy_url: str):
        """Marca un proxy como exitoso"""
        if proxy_url in self.failed_proxies:
            self.failed_proxies.remove(proxy_url)
            logger.debug(f"Proxy removido de lista de fallidos: {proxy_url[:30]}...")
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas de proxies"""
        total = len(self.proxies)
        failed = len(self.failed_proxies)
        available = total - failed
        
        return {
            'total': total,
            'failed': failed,
            'available': available
        }
