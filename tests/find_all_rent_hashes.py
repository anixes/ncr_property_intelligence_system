import asyncio
from playwright.async_api import async_playwright

async def get_city_rent_url(city_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.goto("https://housing.com/", wait_until="load")
        
        # Click the Rent tab
        try:
            await page.locator("div.css-11ywtq0:has-text('Rent')").click()
            await page.wait_for_timeout(1000)
        except:
            print(f"[{city_name}] Could not click rent tab")
            
        # Type the city name
        await page.locator("input[placeholder*='Search']").fill(city_name)
        await page.wait_for_timeout(2000)
        
        # Wait for suggestion drop down
        # Press Enter should go to best matching city
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)
        
        # Press Search button
        try:
            await page.locator("button:has-text('Search')").click()
            await page.wait_for_timeout(4000)
        except:
            pass
            
        url = page.url
        print(f"CITY: {city_name} | RENT URL: {url}")
        
        await browser.close()
        return url

async def main():
    cities = ["New Delhi", "Noida", "Greater Noida", "Ghaziabad", "Faridabad"]
    for c in cities:
        await get_city_rent_url(c)

if __name__ == "__main__":
    asyncio.run(main())
