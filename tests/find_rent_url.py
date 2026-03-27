import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Navigate to housing.com home...")
        await page.goto("https://housing.com/", wait_until="load")
        
        print("Choosing Rent...")
        await page.locator("text=Rent").first.click()
        await page.wait_for_timeout(1000)
        
        print("Typing Gurgaon...")
        await page.locator("input[placeholder*='Search']").fill("Gurgaon")
        await page.wait_for_timeout(2000)
        
        print("Clicking first city suggestion...")
        # Press enter or click the suggestion
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)
        
        print("Clicking search button if needed...")
        try:
            await page.locator("button:has-text('Search')").click(timeout=3000)
            await page.wait_for_timeout(3000)
        except:
            pass
            
        final_url = page.url
        print(f"Final Search URL: {final_url}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
