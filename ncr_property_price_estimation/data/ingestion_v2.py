"""
NCR Housing Scraper — V19.5 [SAFE EXIT UPGRADE]
=============================================
Max Speed, Smart Exits, Clean Data.
- Consecutive Duplicate Exit: If 3 pages have 0 new listings, it exits the slice.
- 6 Cities: Delhi, Gurgaon, Noida, Greater Noida, Ghaziabad, Faridabad
- Global Deduplication: Only saves unique properties across all files.
- Resilient Resume: Saves checkpoint.json every page.
"""

import asyncio
import json
import logging
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from playwright.async_api import async_playwright, Page

# =============================================================================
# CONFIG
# =============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
logger = logging.getLogger("ingestion_v2")

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

RENT_HASHES = {
    "Delhi": "flats-for-rent-in-delhi-india-P6xfqdsey6cc3d95h",
    "Gurgaon": "flats-for-rent-in-gurugram-haryana-P1od1w26jrfqap1jl",
    "Noida": "flats-for-rent-in-noida-uttar-pradesh-P2fqf0dypkiyhifgy",
    "Greater_Noida": "flats-for-rent-in-noida-extension-greater-noida-P5re0m8ks3utkt94f",
    "Ghaziabad": "flats-for-rent-in-ghaziabad-district-uttar-pradesh-P6jenhqnrtl634o1k",
    "Faridabad": "flats-for-rent-in-faridabad-district-haryana-P3ncwuy636vfodgz9",
}

BUY_SLUGS = {
    "Delhi": "new_delhi/new_delhi",
    "Gurgaon": "gurgaon/gurgaon",
    "Noida": "noida/noida",
    "Greater_Noida": "greater_noida/greater_noida",
    "Ghaziabad": "ghaziabad/ghaziabad",
    "Faridabad": "faridabad/faridabad",
}

NCR_CITIES = ["Delhi", "Gurgaon", "Noida", "Greater_Noida", "Ghaziabad", "Faridabad"]
BHK_SLICES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# =============================================================================
# TRACKER
# =============================================================================

class ResilientTracker:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.checkpoint_path = out_dir / "checkpoint.json"
        self.seen_signatures: Set[str] = set()
        self.checkpoint_data = self._load_checkpoint()
        self._prime_deduplication()

    def _load_checkpoint(self):
        if self.checkpoint_path.exists():
            try: return json.loads(self.checkpoint_path.read_text())
            except: return {}
        return {}

    def _prime_deduplication(self):
        logger.info("📡 Priming Smart-Skip Deduplication...")
        files = list(self.out_dir.glob("*.json"))
        for f in files:
            if f.name == "checkpoint.json": continue
            try:
                content = json.loads(f.read_text())
                for rec in content.get("data", []):
                    sig = self.get_signature(rec)
                    self.seen_signatures.add(sig)
            except: continue
        logger.info(f"✅ Loaded {len(self.seen_signatures)} unique property signatures.")

    def get_signature(self, rec: Dict) -> str:
        text = f"{rec.get('title_raw')}|{rec.get('price_text')}|{rec.get('area_text')}"
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def is_new(self, rec: Dict) -> bool:
        sig = self.get_signature(rec)
        if sig in self.seen_signatures: return False
        self.seen_signatures.add(sig)
        return True

    def save_checkpoint(self, is_rent: bool, city: str, bhk: int, page: int):
        key = "rent" if is_rent else "buy"
        if key not in self.checkpoint_data: self.checkpoint_data[key] = {}
        self.checkpoint_data[key] = {"city": city, "bhk": bhk, "page": page, "ts": datetime.now().isoformat()}
        self.checkpoint_path.write_text(json.dumps(self.checkpoint_data, indent=2), encoding="utf-8")

    def get_last_state(self, is_rent: bool):
        key = "rent" if is_rent else "buy"
        state = self.checkpoint_data.get(key, {})
        return state.get("city"), state.get("bhk"), state.get("page", 0)

# =============================================================================
# EXTRACTOR & ENGINE
# =============================================================================

class HousingExtractor:
    @staticmethod
    async def extract(page: Page, city: str, bhk: int, is_rent: bool = False) -> List[Dict]:
        js_args = {"city": city, "bhkText": f"{bhk} BHK", "type": "rent" if is_rent else "buy"}
        js_code = """
        (args) => {
            const data = [];
            const cards = [...document.querySelectorAll('article, div[class*="item"], div[class*="Card"]')];
            cards.forEach(card => {
                try {
                    const text = card.innerText || "";
                    if (text.length < 50) return;
                    const a = card.querySelector('a[href*="/p/"]');
                    const titleEl = card.querySelector('h1, h2, h3, div[class*="title"]');
                    const title = titleEl ? titleEl.innerText.trim() : "Untitled";
                    const price = [...card.querySelectorAll('div, span, b')].find(el => el.innerText.includes('₹'))?.innerText.trim() || "";
                    const area = [...card.querySelectorAll('div, span')].find(el => el.innerText.toLowerCase().includes('sq.ft'))?.innerText.trim() || "";
                    let hint = "Independent";
                    const possibleLocs = [...card.querySelectorAll('div')].filter(d => d.innerText.length > 3 && d.innerText.length < 40);
                    if (possibleLocs.length > 0) hint = possibleLocs[0].innerText.split('\\n')[0].trim();
                    if (price || area) {
                        data.push({
                            title_raw: title,
                            price_text: price,
                            area_text: area,
                            city: args.city,
                            bhk_text: args.bhkText,
                            listing_type: args.type,
                            society_hint: hint,
                            description_raw: text,
                            source_url: a ? a.href : "",
                            scraped_at: new Date().toISOString()
                        });
                    }
                } catch(e) {}
            });
            return data;
        }
        """
        try: return await page.evaluate(js_code, js_args)
        except: return []

    @staticmethod
    async def next_page(page: Page) -> bool:
        for sel in ["a[aria-label='Next']", "button:has-text('Next')", "div[class*='next']"]:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    await asyncio.sleep(4)
                    return True
            except: continue
        return False

class IngestionEngine:
    def __init__(self, out_dir: Path, max_pages: int = 100):
        self.tracker = ResilientTracker(out_dir)
        self.max_pages = max_pages

    async def run(self, is_rent: bool = False):
        cities = NCR_CITIES
        r_city, r_bhk, r_page = self.tracker.get_last_state(is_rent)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, channel="chrome")
            context = await browser.new_context(user_agent=random.choice(UA_POOL))
            page = await context.new_page()

            for city in cities:
                if is_rent and city == "Delhi": 
                    continue
                
                cfg = RENT_HASHES if is_rent else BUY_SLUGS
                if city not in cfg: continue
                if r_city and NCR_CITIES.index(city) < NCR_CITIES.index(r_city): continue

                for bhk in BHK_SLICES:
                    if r_city == city and bhk < r_bhk: continue
                    
                    slug = cfg[city]
                    url = f"https://housing.com/{'rent' if is_rent else 'in/buy'}/{slug}?bhk={bhk}"
                    logger.info(f"🚀 {city} | {bhk} BHK | {url}")
                    
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        await asyncio.sleep(5)
                        
                        consecutive_dupes = 0
                        for p_idx in range(self.max_pages):
                            if r_city == city and r_bhk == bhk and p_idx < r_page: continue
                            
                            logger.info(f"  📄 Page {p_idx+1}")
                            raw_recs = await HousingExtractor.extract(page, city, bhk, is_rent)
                            new_recs = [r for r in raw_recs if self.tracker.is_new(r)]
                            
                            if new_recs:
                                consecutive_dupes = 0 # Reset counter on fresh data
                                ts = int(datetime.now().timestamp())
                                fname = f"{city}_{bhk}_{'rent' if is_rent else 'buy'}_p{p_idx+1}_{ts}.json"
                                (self.tracker.out_dir / fname).write_text(json.dumps({"data": new_recs}, indent=2), encoding="utf-8")
                                logger.info(f"    💾 Saved {len(new_recs)} NEW records.")
                            else:
                                consecutive_dupes += 1
                                logger.warning(f"    ⏩ Skipping page {p_idx+1} (All duplicates). Dupes in a row: {consecutive_dupes}")
                            
                            self.tracker.save_checkpoint(is_rent, city, bhk, p_idx)
                            
                            # SMART EXIT: If 3 consecutive pages have NO new data, assume listing ended
                            if consecutive_dupes >= 3:
                                logger.info(f"  🛑 Inventory Exhausted for {city} {bhk}BHK. Moving to next slice.")
                                break

                            if not await HousingExtractor.next_page(page): break
                            
                        r_city, r_bhk, r_page = None, None, 0
                    except Exception as e:
                        logger.error(f"  Error: {e}")
                        continue
            await browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rent", action="store_true")
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args()
    engine = IngestionEngine(Path("./data/external"), max_pages=args.max_pages)
    asyncio.run(engine.run(is_rent=args.rent))
