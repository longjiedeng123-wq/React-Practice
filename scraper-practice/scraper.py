import asyncio
from playwright.async_api import async_playwright
import httpx

async def enter_zip_code(page) -> None:
    try:
        print("Checking for location modal...")
        
        # Target the exact placeholder text you found in the DOM!
        zip_input = page.locator("input[placeholder='Enter zip code']")
        
        # Wait up to 5 seconds for the modal to pop up
        await zip_input.wait_for(timeout=5000)
        
        # Fill in the Tustin zip code
        await zip_input.fill("92780")
        
        # Instead of clicking the button, hitting "Enter" is often faster and bypasses disabled states
        await zip_input.press("Enter")
        
        print("Zip code entered automatically!")
        
        # Wait 2 seconds for the website to unlock and load the real images
        await page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f"Error happening during zip input: {e}")

async def scrape_ad_images():
    image_paths = []
    Link_99Ranch = "https://www.99ranch.com/stores/promotions/1259"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(Link_99Ranch)

        await enter_zip_code(page)

        tabs = await page.locator("img[alt='poster']").all()
        downloaded_urls = set() 
        count = 1
        last_url = ""
        async with httpx.AsyncClient() as client:
            for tab in tabs:
                try:
                    await tab.evaluate("node => node.click()")
                    
                    full_url : str = ""
                    
                    for _ in range(10):
                        await page.wait_for_timeout(500)
                        main_image = page.locator("img[alt='Zoomable']").first
                        temp_url : str = await main_image.get_attribute("src") # type: ignore
                        
                        if temp_url and not temp_url.startswith("data:image") and temp_url != last_url:
                            full_url = temp_url
                            last_url = full_url 
                            break 
                    
                    if not full_url:
                        continue

                    if full_url.startswith("/"):
                        full_url = "https://www.99ranch.com" + full_url

                    if full_url in downloaded_urls:
                        continue

                    downloaded_urls.add(full_url)
                    
                    response = await client.get(full_url)
                    image_name = f"weekly_ad_{count}.jpg"

                    with open(image_name, "wb") as file:
                        file.write(response.content)

                    image_paths.append(image_name)
                    count += 1
                    
                except Exception as e:
                    print(f"Skipping a tab due to error: {e}")
        
        await browser.close()

        return image_paths