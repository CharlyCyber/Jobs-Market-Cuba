#!/usr/bin/env python3

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.scraper_manager import ScraperManager
from bot.utils.formatter import HTMLFormatter
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


async def test_scraping():
    logger.info("=" * 60)
    logger.info("Testing Scraper - Cuba Jobs Bot")
    logger.info("=" * 60)
    
    manager = ScraperManager()
    
    logger.info("\nStarting scraping process...")
    offers = await manager.scrape_all()
    
    logger.info(f"\n{'=' * 60}")
    logger.info(f"RESULTS")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total offers found: {len(offers)}")
    
    if offers:
        logger.info("\nSample offers:")
        for i, offer in enumerate(offers[:5], 1):
            logger.info(f"\n{i}. {offer['title']}")
            logger.info(f"   Company: {offer['company']}")
            logger.info(f"   Source: {offer['source']}")
            logger.info(f"   Link: {offer['link']}")
            logger.info(f"   Description: {offer['description'][:100]}...")
        
        formatter = HTMLFormatter()
        html = formatter.format_job_offers(offers)
        
        output_file = "test_output.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"<html><body>{html}</body></html>")
        
        logger.info(f"\n✅ HTML output saved to: {output_file}")
    else:
        logger.warning("\n❌ No offers found matching the filters")
    
    logger.info(f"\n{'=' * 60}")
    logger.info("Test completed!")
    logger.info(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(test_scraping())
