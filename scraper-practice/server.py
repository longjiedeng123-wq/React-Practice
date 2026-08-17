from fastapi import FastAPI
from scraper import scrape_ad_images
from ai_extractor import extract_prices
app = FastAPI()

@app.get("/")
def root():
    print("starting to fetch data...")
    all_products = extract_prices(scrape_ad_images())
    print("Data fetch complete-------")
    return {"data" : all_products}

