import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        url = "https://housing.com/rent/property-for-rent-in-gurgaon"
        print(f"Opening {url}...")
        await page.goto(url, wait_until="load", timeout=60000)
        await asyncio.sleep(8)
        
        # We need to scroll a bit to trigger rendering
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(2)
        
        counts = await page.evaluate('''() => ({
            articles: document.querySelectorAll("article").length
        })''')
        print(f"Counts: {counts}")
        
        if counts['articles'] > 0:
            html = await page.evaluate('''() => {
                const card = document.querySelector("article");
                return card.outerHTML;
            }''')
            with open("d:\\DATA SCIENCE\\ncr_property_price_estimation\\tests\\rent_article_dump.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Dumped first article HTML.")
        else:
            print("No articles found to dump.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
