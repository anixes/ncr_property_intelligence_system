import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless False to exactly match ingestion
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Inject standard stealth scripts (simplified)
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Opening rental page...")
        await page.goto("https://housing.com/rent/property-for-rent-in-gurgaon", wait_until="load", timeout=60000)
        
        print("Scrolling...")
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(2000)
        await page.mouse.wheel(0, 1000)
        await page.wait_for_timeout(5000) # Give React plenty of time to hydrate
        
        print("Extracting full text...")
        text = await page.evaluate("document.body.innerText")
        with open("d:\\DATA SCIENCE\\ncr_property_price_estimation\\tests\\rent_full_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("Done. Saved to rent_full_text.txt.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
