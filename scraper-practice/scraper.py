from playwright.sync_api import sync_playwright
import requests

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://h5.awsprod.99ranch.com/stores/ad/1009")
    
    image_elements = page.locator("img[alt='poster']").all()

    count = 1

    for image_element in image_elements:

        partial_url = image_element.get_attribute("src")
    
        full_url = "https://h5.awsprod.99ranch.com" + partial_url
        print("Downloading from:", full_url)
        
        response = requests.get(full_url)
        
        with open(f"weekly_ad_{count}.jpg", "wb") as file:
            file.write(response.content)
            
        print("Image downloaded successfully!")

        count += 1
    
    browser.close()