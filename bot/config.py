import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    REQUEST_DELAY = int(os.getenv("REQUEST_DELAY", "2"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    USE_SELENIUM = os.getenv("USE_SELENIUM", "false").lower() == "true"
    
    HTTP_PROXY = os.getenv("HTTP_PROXY")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY")
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    REVOLICO_URL = os.getenv(
        "REVOLICO_URL",
        "https://www.revolico.com/empleos"
    )
    CUBISIMA_MARKETING_URL = os.getenv(
        "CUBISIMA_MARKETING_URL",
        "https://www.cubisima.com/empleos/ofertas/marketing?categoriaestricta"
    )
    CUBISIMA_DESIGN_URL = os.getenv(
        "CUBISIMA_DESIGN_URL",
        "https://www.cubisima.com/empleos/ofertas/diseno?categoriaestricta"
    )
    CUBISIMA_IT_URL = os.getenv(
        "CUBISIMA_IT_URL",
        "https://www.cubisima.com/empleos/ofertas/informatica-Cibernetica?categoriaestricta"
    )
    CUCODERS_URL = os.getenv(
        "CUCODERS_URL",
        "https://cucoders.dev/empleos/"
    )
    
    @staticmethod
    def get_filter_keywords() -> List[str]:
        keywords_str = os.getenv(
            "FILTER_KEYWORDS",
            "inteligencia artificial,ia,ai,machine learning,ml,deep learning,"
            "diseño,design,designer,redacción,redactor,writer,content,contenido,"
            "automatización,automation,rpa,bot"
        )
        return [kw.strip().lower() for kw in keywords_str.split(",")]
    
    @staticmethod
    def get_proxies():
        proxies = {}
        if Config.HTTP_PROXY:
            proxies["http"] = Config.HTTP_PROXY
        if Config.HTTPS_PROXY:
            proxies["https"] = Config.HTTPS_PROXY
        return proxies if proxies else None
    
    @staticmethod
    def validate():
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required in .env file")
