from fastapi import FastAPI
from scraper import scrape_ad_images
from ai_extractor import extract_prices
app = FastAPI()

@app.get("/")
def root():
    {"Hello" : "world"}

@app.get("/api/prices")
def get_grocery_prices():
    print("API called: Starting scraping process...")

    image_paths = scrape_ad_images()

    print("scraping complete...")

    all_products = extract_prices(image_paths)
    
    print("Data fetch complete-------")

    return {
        "status" : "success",
        "total_items" : len(all_products),
        "data" : all_products
    }