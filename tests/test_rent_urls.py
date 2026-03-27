import asyncio
from playwright.async_api import async_playwright

async def get_url():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # We start on a known working URL
        await page.goto("https://housing.com/in/buy/gurgaon/1bhk-gurgaon", wait_until="load")
        await page.wait_for_timeout(3000)
        
        # Click the Rent button in the top navigation or search bar!
        print("Clicking Rent...")
        try:
            # Look for the pill that says Rent
            await page.locator("div:text('Rent')").first.click()
            await page.wait_for_timeout(2000)
            
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)
            print("URL IS:", page.url)
        except Exception as e:
            print(e)
            
        print("Final URL:", page.url)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_url())
