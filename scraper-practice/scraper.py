from playwright.sync_api import sync_playwright
import requests

def enter_zip_code(page) -> None:
    try:
        print("Checking for location modal...")
        
        # Target the exact placeholder text you found in the DOM!
        zip_input = page.locator("input[placeholder='Enter zip code']")
        
        # Wait up to 5 seconds for the modal to pop up
        zip_input.wait_for(timeout=5000)
        
        # Fill in the Tustin zip code
        zip_input.fill("92780")
        
        # Instead of clicking the button, hitting "Enter" is often faster and bypasses disabled states
        zip_input.press("Enter")
        
        print("Zip code entered automatically!")
        
        # Wait 2 seconds for the website to unlock and load the real images
        page.wait_for_timeout(2000)
        
    except Exception as e:
        print(f"Error happening during zip input: {e}")

def scrape_ad_images():
    image_paths = []
    Link_99Ranch = "https://www.99ranch.com/stores/promotions/1259"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(Link_99Ranch)

        enter_zip_code(page)

        tabs = page.locator("img[alt='poster']").all()
        downloaded_urls = set() 
        count = 1
        last_url = ""

        for tab in tabs:
            try:
                tab.evaluate("node => node.click()")
                
                full_url = None
                
                for _ in range(10):
                    page.wait_for_timeout(500)
                    main_image = page.locator("img[alt='Zoomable']").first
                    temp_url = main_image.get_attribute("src")
                    
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
                
                response = requests.get(full_url)
                image_name = f"weekly_ad_{count}.jpg"

                with open(image_name, "wb") as file:
                    file.write(response.content)

                image_paths.append(image_name)
                count += 1
                
            except Exception as e:
                print(f"Skipping a tab due to error: {e}")
        
        browser.close()

        return image_paths