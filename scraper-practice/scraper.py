from playwright.sync_api import sync_playwright
import requests

def scrape_ad_images():
    image_paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.99ranch.com/stores/promotions/1259")
        
        image_elements = page.locator("img[alt='Zoomable']").all()

        count = 1

        for image_element in image_elements:

            full_url = image_element.get_attribute("src")

            if not full_url:
                print("This Poster not found")
                continue

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