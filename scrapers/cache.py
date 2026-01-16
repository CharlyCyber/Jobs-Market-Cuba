"""
Cache Manager - Evita requests innecesarias a sitios ya scrapeados
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class CacheManager:
    
    def __init__(self, cache_dir: str = 'cache', ttl_hours: int = 2):
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"CacheManager inicializado: dir={cache_dir}, TTL={ttl_hours}h")
    
    def _get_cache_key(self, url: str) -> str:
        """Genera clave única para URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Dict]:
        """Obtiene datos cacheados si existen y son válidos"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data['timestamp'])
            
            # Verificar si el cache expiró
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expirado para: {url[:50]}...")
                cache_file.unlink()
                return None
            
            logger.info(f"Cache HIT para: {url[:50]}...")
            return data['content']
            
        except Exception as e:
            logger.error(f"Error leyendo cache: {e}")
            return None
    
    def set(self, url: str, content: Dict):
        """Guarda datos en cache"""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'url': url[:100]  # Guardar URL corta para referencia
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cache guardado: {cache_key[:20]}...")
            
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def clear(self):
        """Limpia todo el cache"""
        try:
            for file in self.cache_dir.glob('*.json'):
                file.unlink()
            logger.info("Cache limpiado exitosamente")
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estadísticas del cache"""
        try:
            cache_files = list(self.cache_dir.glob('*.json'))
            
            valid_count = 0
            expired_count = 0
            now = datetime.now()
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    cached_time = datetime.fromisoformat(data['timestamp'])
                    
                    if now - cached_time <= self.ttl:
                        valid_count += 1
                    else:
                        expired_count += 1
                        
                except:
                    expired_count += 1
            
            return {
                'total_files': len(cache_files),
                'valid': valid_count,
                'expired': expired_count
            }
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas: {e}")
            return {'total_files': 0, 'valid': 0, 'expired': 0}
