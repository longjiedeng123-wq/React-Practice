from playwright.sync_api import sync_playwright
import requests

def scrape_ad_images():
    image_paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.99ranch.com/stores/promotions/1259")

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
            
        except Exception:
            print("No location modal detected within 5 seconds. Proceeding...")

        image_elements = page.locator("img[alt='poster']").all()

        count = 1
        

        for image_element in image_elements:

            partial_url : str = image_element.get_attribute("src") # type: ignore

            if not partial_url.startswith("/"):

                print(f"~~~~~~~~~~~~This Poster not found, skipping to next one{partial_url}~~~~~~~~~")
                continue

            full_url = "https://www.99ranch.com"+ partial_url

            print("Downloading from:", full_url)
            
            response = requests.get(full_url)
            image_name = f"weekly_ad_{count}.jpg"

            with open(image_name, "wb") as file:
                file.write(response.content)

            image_paths.append(image_name)

            print("Image downloaded successfully!")

            count += 1
        
        browser.close()

        return image_paths