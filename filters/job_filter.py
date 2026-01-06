from typing import List, Dict
from bot.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class JobFilter:
    
    def __init__(self):
        self.keywords = Config.get_filter_keywords()
        logger.info(f"Initialized JobFilter with {len(self.keywords)} keywords")
    
    def filter_offers(self, offers: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not offers:
            return []
        
        filtered = []
        for offer in offers:
            if self._matches_filter(offer):
                filtered.append(offer)
        
        logger.info(f"Filtered {len(offers)} offers down to {len(filtered)} relevant offers")
        return filtered
    
    def _matches_filter(self, offer: Dict[str, str]) -> bool:
        title = offer.get('title', '').lower()
        description = offer.get('description', '').lower()
        company = offer.get('company', '').lower()
        
        combined_text = f"{title} {description} {company}"
        
        for keyword in self.keywords:
            if keyword in combined_text:
                logger.debug(f"Offer matched keyword: {keyword}")
                return True
        
        return False
