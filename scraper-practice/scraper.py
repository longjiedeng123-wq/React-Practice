from playwright.sync_api import sync_playwright
import requests

def scrape_ad_images():
    image_paths = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://h5.awsprod.99ranch.com/stores/ad/1009")
        
        image_elements = page.locator("img[alt='poster']").all()

        count = 1

        for image_element in image_elements:

            partial_url = image_element.get_attribute("src")

            if not partial_url:
                print("This Poster not found")
                continue

            full_url = "https://h5.awsprod.99ranch.com" + partial_url
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