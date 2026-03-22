import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async

# =============================================================================
# V7 GOLD STANDARD - INGESTION ENGINE (PLAYWRIGHT)
# =============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class BaseAgentStrategy(ABC):
    """Abstract interface for site-specific extraction logic."""
    @abstractmethod
    def build_search_url(self, city: str, is_rent: bool = False) -> str:
        """Construct the search URL for the target city/category."""
        pass

    @abstractmethod
    async def extract_listings(self, page: Page) -> List[Dict[str, Any]]:
        """Extract property metadata from the search results page."""
        pass

    @abstractmethod
    async def handle_pagination(self, page: Page) -> bool:
        """Click 'Next' button if available and return True."""
        pass

class HousingStrategy(BaseAgentStrategy):
    """Extraction strategy for Housing.com."""
    def build_search_url(self, city: str, is_rent: bool = False) -> str:
        # Simplified dynamic URL construction for NCR
        cities = {"gurgaon": "gurgaon", "noida": "noida", "ghaziabad": "ghaziabad", "faridabad": "faridabad"}
        slug = cities.get(city.lower(), city.lower())
        return f"https://housing.com/{'rent' if is_rent else 'buy'}-flats-in-{slug}"

    async def extract_listings(self, page: Page) -> List[Dict[str, Any]]:
        # This will be refined with actual CSS selectors from the site
        logger.info("Extracting listings from Housing.com...")
        return [] # selectors will be added here

    async def handle_pagination(self, page: Page) -> bool:
        return False # logic for 'Next' button

class PlaywrightScraper:
    """Industrial-Grade Scraper optimized for EC2 Free Tier (Low Memory)."""
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.raw_dir = output_dir / "tinyfish" # Storage path for audit traces
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.batch_id = f"batch_{int(datetime.now().timestamp())}"

    async def run(self, strategy: BaseAgentStrategy, city: str, is_rent: bool = False, max_pages: int = 1):
        """Main execution loop with aggressive memory management for Free Tier."""
        async with async_playwright() as p:
            # Headless mode is essential for EC2 (no GUI)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            await stealth_async(page)
            
            url = strategy.build_search_url(city, is_rent)
            logger.info(f"Navigating to {url}")
            
            records = []
            try:
                # 60s timeout for slow EC2 connections
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                for p_idx in range(max_pages):
                    logger.info(f"Processing page {p_idx + 1}/{max_pages}")
                    batch_data = await strategy.extract_listings(page)
                    records.extend(batch_data)
                    
                    if not await strategy.handle_pagination(page):
                        break
                    
                    # Polite delay (Free Tier friendly)
                    await asyncio.sleep(2)
            
            except Exception as e:
                logger.error(f"Failed to scrape {city}: {e}")
            
            finally:
                # Save Raw Audit Trace (Requirement V7)
                site_name = strategy.__class__.__name__.replace("Strategy", "").lower()
                self._save_raw_batch(site_name, city, records)
                await browser.close()

    def _save_raw_batch(self, site: str, city: str, records: List[Dict[str, Any]]):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_path = self.raw_dir / site / city
        batch_path.mkdir(parents=True, exist_ok=True)
        
        file_path = batch_path / f"{ts}.json"
        
        payload = {
            "metadata": {
                "site": site,
                "city": city,
                "timestamp": ts,
                "batch_id": self.batch_id,
                "record_count": len(records),
                "pipeline_version": "v7.0"
            },
            "data": records
        }
        
        with open(file_path, "w") as f:
            json.dump(payload, f, indent=4)
        
        logger.info(f"Saved {len(records)} raw records to {file_path}")

if __name__ == "__main__":
    # Test script setup
    scraper = PlaywrightScraper(Path("./data/raw"))
    asyncio.run(scraper.run(HousingStrategy(), "Gurgaon", max_pages=1))
