import asyncio
from playwright.async_api import async_playwright

async def intercept_albertsons_ad():
    
    async with async_playwright() as p:
        # Launch the browser in visible mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Navigating to Albertsons base URL...")
        await page.goto("https://www.albertsons.com/weeklyad")
        
        # Temporary pause to allow the page to render before our next step
        await page.wait_for_timeout(3000)

        cookie_btn = page.locator("button:has-text('Continue with all')")
        await cookie_btn.wait_for(state="visible", timeout=10000)
        await cookie_btn.click()
        await page.wait_for_timeout(3000)

        print("Clicking region text to open location modal...")
        location_btn = page.locator(".s_nav_fulfillment_address-text:visible").first
        await location_btn.wait_for(state="visible", timeout=10000)
        await location_btn.click()
        await page.wait_for_timeout(3000)

        print("Entering ZIP code...")
        zip_input = page.locator("input[placeholder*='ZIP Code']")
        await zip_input.wait_for(state="visible", timeout=10000)
        await zip_input.fill("92780")
        print("Submitting search...")
        await zip_input.press("Enter")
        await page.wait_for_timeout(3000)

        print("Selecting local store...")
        select_btn = page.get_by_text("Select", exact=True).first
        await select_btn.wait_for(state="visible", timeout=10000)
        await select_btn.click()
        await page.wait_for_timeout(3000)

        # Cleanup
        await browser.close()


    


    