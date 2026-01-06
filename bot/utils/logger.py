import logging
import sys
from bot.config import Config


def setup_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
