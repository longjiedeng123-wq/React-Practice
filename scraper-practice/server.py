from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from scraper import scrape_ad_images
from ai_extractor import extract_prices

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url : str = os.environ.get("SUPABASE_URL", "")
key : str = os.environ.get("SUPABASE_KEY", "")
supabase : Client = create_client(url, key)

app = FastAPI()

frontend_urls_str = os.environ.get("FRONTEND_URLS", "")
origins = frontend_urls_str.split(",") if frontend_urls_str else []

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
        return response.data[0]["id"] # type: ignore

    new_store = supabase.table("stores").insert({"name": store_name}).execute()
    return new_store.data[0]["id"] # type: ignore

def save_grocery_items(store_id: str, extracted_items: list):
    product_batch = []

    for item in extracted_items:
        if not item.get("english_name"):
            continue

        product_batch.append({
            "store_id": store_id,
            "english_name": item["english_name"],
            "chinese_name": item.get("chinese_name"),
            "base_unit_type": item.get("unit")
        })

        if product_batch:
            product_response = supabase.table("products").upsert(
                product_batch,
                on_conflict="store_id,english_name"
            ).execute()

            print(f"Upserted {len(product_response.data)} products.")

        product_id_map = {row["english_name"]: row["id"] for row in product_response.data} # type: ignore

        price_batch = []

        for item in extracted_items:
            english_name = item.get("english_name")

            if not english_name or english_name not in product_id_map:
                continue

            price_batch.append({
                "product_id": product_id_map[english_name],
                "original_price": item.get("original_price"),
                "discount_price": item.get("discount_price"),
                "valid_dates": item.get("valid_dates"),
                "taxable": item.get("taxable"),
                "has_crv": item.get("has_crv")
            })

            print(f"Prepared {len(price_batch)} price records for batch insert.")

        if price_batch:
            price_response = supabase.table("price_history").insert(price_batch).execute()
            print(f"Inserted {len(price_response.data)} price records.")    

            
async def run_scraping_pipeline():
    image_paths = await scrape_ad_images()

    print("~~~~~~~~scrape success~~~~~~~")
    all_products = await extract_prices(image_paths)

    store_id = await asyncio.to_thread(get_or_create_store, "99 Ranch")
    await asyncio.to_thread(save_grocery_items, store_id, all_products)


@app.get("/")
def root():
    return {"Hello" : "world"}

@app.get("/api/prices")
async def get_grocery_prices(background_tasks: BackgroundTasks):
    
    print("API called: Starting scraping process...")

    background_tasks.add_task(run_scraping_pipeline)

    
    return {
        "status" : "success",
        "message" : "Scraping started in the background. Data will be available soon."
    }

@app.get('/api/products')
def get_saved_products():

    response = supabase.table("products").select(
        "english_name, chinese_name, base_unit_type, price_history(original_price, discount_price, valid_dates, taxable, has_crv)"
    ).execute()

    formatted_products = []
    print(f"~~~~~~~~~~~response DATA: {response.data} ~~~~~~~~~~~")
    for product in response.data:
        p : dict = product # type: ignore
        history : list = p.get("price_history", [])

        latest_price : dict = history[0] if history else {}

        formatted_products.append({
            "english_name": p.get("english_name"),
            "chinese_name": p.get("chinese_name"),
            "unit": p.get("base_unit_type"),
            "original_price": latest_price.get("original_price"),
            "discount_price": latest_price.get("discount_price"),
            "taxable": latest_price.get("taxable"),
            "has_crv": latest_price.get("has_crv")
        })

    return {
        "status": "success",
        "total_items": len(formatted_products),
        "data": formatted_products
    }