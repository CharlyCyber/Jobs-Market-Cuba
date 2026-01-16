"""
Circuit Breaker Pattern - Protege contra cascadas de fallos
Cuando un scraper falla muchas veces seguidas, lo bloquea temporalmente
"""

from datetime import datetime, timedelta
from enum import Enum
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Operación normal
    OPEN = "open"           # Falla detectada, bloquear
    HALF_OPEN = "half_open"  # Probar si se recuperó


class CircuitBreaker:
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout)
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.next_attempt = datetime.min
        self.name = "CircuitBreaker"
        
        logger.info(f"CircuitBreaker inicializado: threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def call(self, func):
        """Ejecuta función con protección de circuit breaker"""
        # Verificar si el circuito está abierto
        if self.state == CircuitState.OPEN:
            if datetime.now() >= self.next_attempt:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker pasó a HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker está OPEN. Reintentar en {(self.next_attempt - datetime.now()).seconds}s")
        
        try:
            result = func()
            
            # Si estaba en HALF_OPEN y tuvo éxito, cerrar circuito
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                logger.info(f"Circuit breaker cerrado exitosamente")
            
            return result
            
        except Exception as e:
            self.failures += 1
            logger.warning(f"Fallo en circuit breaker ({self.failures}/{self.failure_threshold}): {str(e)[:100]}")
            
            # Si alcanza el umbral de fallos, abrir circuito
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.next_attempt = datetime.now() + self.recovery_timeout
                logger.error(f"Circuit breaker ABIERTO por {self.recovery_timeout.seconds} segundos")
            
            raise e
    
    def reset(self):
        """Reinicia el circuit breaker manualmente"""
        self.failures = 0
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker reiniciado manualmente")
    
    def get_state(self) -> CircuitState:
        """Retorna el estado actual"""
        return self.state
    
    def get_stats(self) -> dict:
        """Retorna estadísticas"""
        return {
            'state': self.state.value,
            'failures': self.failures,
            'threshold': self.failure_threshold,
            'next_attempt': self.next_attempt.isoformat() if self.next_attempt != datetime.min else None
        }
