"""
Metrics Manager - Métricas de scraping para monitoreo
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class ScrapingMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    retry_requests: int = 0
    proxy_failures: int = 0
    average_response_time: float = 0.0
    start_time: Optional[datetime] = None
    
    def record_success(self, response_time: float):
        """Registra una request exitosa"""
        self.total_requests += 1
        self.successful_requests += 1
        
        if self.start_time is None:
            self.start_time = datetime.now()
        
        # Actualizar promedio móvil
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            # Promedio con peso del 90% al valor anterior
            self.average_response_time = (
                self.average_response_time * 0.9 + response_time * 0.1
            )
    
    def record_failure(self, reason: str = ""):
        """Registra una request fallida"""
        self.total_requests += 1
        self.failed_requests += 1
        logger.debug(f"Request fallida ({self.failed_requests}): {reason[:50]}...")
    
    def record_cache_hit(self):
        """Registra un hit de cache"""
        self.cached_requests += 1
        logger.debug(f"Cache hit #{self.cached_requests}")
    
    def record_retry(self):
        """Registra un reintento"""
        self.retry_requests += 1
        logger.debug(f"Retry #{self.retry_requests}")
    
    def record_proxy_failure(self):
        """Registra un fallo de proxy"""
        self.proxy_failures += 1
        logger.debug(f"Proxy failure #{self.proxy_failures}")
    
    def get_success_rate(self) -> float:
        """Calcula tasa de éxito"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_cache_hit_rate(self) -> float:
        """Calcula tasa de cache hits"""
        if self.total_requests == 0:
            return 0.0
        return (self.cached_requests / self.total_requests) * 100
    
    def get_summary(self) -> Dict[str, str]:
        """Retorna resumen de métricas"""
        elapsed_time = None
        if self.start_time:
            elapsed_time = datetime.now() - self.start_time
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'cached_requests': self.cached_requests,
            'retry_requests': self.retry_requests,
            'proxy_failures': self.proxy_failures,
            'success_rate': f"{self.get_success_rate():.2f}%",
            'cache_hit_rate': f"{self.get_cache_hit_rate():.2f}%",
            'avg_response_time': f"{self.average_response_time:.2f}s",
            'elapsed_time': str(elapsed_time) if elapsed_time else "N/A"
        }
    
    def print_summary(self):
        """Imprime resumen de métricas"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 MÉTRICAS DE SCRAPING")
        print("="*60)
        print(f"✅ Requests exitosas:  {summary['successful_requests']}")
        print(f"❌ Requests fallidas:  {summary['failed_requests']}")
        print(f"💾 Cache hits:       {summary['cached_requests']}")
        print(f"🔄 Reintentos:       {summary['retry_requests']}")
        print(f"🌐 Fallos de proxy:  {summary['proxy_failures']}")
        print(f"📈 Tasa de éxito:     {summary['success_rate']}")
        print(f"💾 Tasa de cache:    {summary['cache_hit_rate']}")
        print(f"⏱️  Tiempo promedio:    {summary['avg_response_time']}")
        if summary['elapsed_time'] != "N/A":
            print(f"⏰ Tiempo total:      {summary['elapsed_time']}")
        print("="*60 + "\n")
