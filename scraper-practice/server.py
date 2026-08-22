from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraper import scrape_ad_images
from ai_extractor import extract_prices

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url : str = os.environ.get("SUPABASE_URL")
key : str = os.environ.get("SUPABASE_KEY")
supabase : Client = create_client(url, key)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://linkong666.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

cached_grocery_data = None

@app.get("/")
def root():
    return {"Hello" : "world"}

@app.get("/api/prices")
def get_grocery_prices():
    global cached_grocery_data

    if cached_grocery_data is not None:
        print("Returning stored data, no scraping is needed")
        return {
            "status" : "success",
            "total_items" : len(cached_grocery_data),
            "data" : cached_grocery_data
        }
    print("API called: Starting scraping process...")

    image_paths = scrape_ad_images()

    print("scraping complete...")

    all_products = extract_prices(image_paths)
    
    print("Data fetch complete-------")

    cached_grocery_data = all_products

    return {
        "status" : "success",
        "total_items" : len(all_products),
        "data" : all_products
    }

