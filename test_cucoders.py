#!/usr/bin/env python3

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.cucoders_scraper import CucodersScraper
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_cucoders_only():
    logger.info("=" * 60)
    logger.info("Testing CuCoders Scraper Only")
    logger.info("=" * 60)
    
    scraper = CucodersScraper()
    
    logger.info("Starting CuCoders scraping...")
    offers = scraper.scrape()
    
    logger.info(f"\n{'=' * 60}")
    logger.info(f"RESULTS")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total offers found: {len(offers)}")
    
    if offers:
        logger.info("\nOffers:")
        for i, offer in enumerate(offers, 1):
            logger.info(f"\n{i}. {offer['title']}")
            logger.info(f"   Company: {offer['company']}")
            logger.info(f"   Source: {offer['source']}")
            logger.info(f"   Link: {offer['link']}")
            logger.info(f"   Description: {offer['description'][:100]}...")
    else:
        logger.warning("❌ No offers found")
    
    logger.info(f"\n{'=' * 60}")
    logger.info("Test completed!")
    logger.info(f"{'=' * 60}\n")

if __name__ == "__main__":
    asyncio.run(test_cucoders_only())