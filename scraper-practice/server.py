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
def get_or_create_store(store_name: str) -> str:
    response = supabase.table("stores").select("id").eq("name", store_name).execute()

    if response.data:
        return response.data[0]["id"]

    new_store = supabase.table("stores").insert({"name": store_name}).execute()
    return new_store.data[0]["id"]

def save_grocery_items(store_id: str, extracted_items: list):
    for item in extracted_items:
        if not item.get("english_name"):
            continue

        product_response = supabase.table("products").select("id").eq("store_id", store_id).eq("english_name", item["english_name"]).execute()

        if product_response.data:
            product_id = product_response.data[0]["id"]
        else:
            new_product = supabase.table("products").insert({
                "store_id": store_id,
                "english_name": item["english_name"],
                "chinese_name": item.get("chinese_name"),
                "base_unit_type": item.get("unit")
            }).execute()
            product_id = new_product.data[0]["id"]

        supabase.table("price_history").insert({
            "product_id": product_id,
            "original_price": item.get("original_price"),
            "discount_price": item.get("discount_price"),
            "valid_dates": item.get("valid_dates"),
            "taxable": item.get("taxable"),
            "has_crv": item.get("has_crv")
        }).execute()
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

