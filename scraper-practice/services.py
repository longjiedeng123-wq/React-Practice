import asyncio
from ranch_scraper import scrape_ad_images
from albertsons_scraper import intercept_albertsons_ad
from ai_extractor import extract_prices
from database import get_or_create_store, save_grocery_items

job_state = {
    "status": "idle" # Phases: "idle" -> "scraping" -> "processing"
}

async def run_albertsons_pipeline(connect_url: str = None):
    try:
        job_state["status"] = "scraping" # <-- Phase 1
        print("Starting Albertsons scraping pipeline...")
        
        sanitized_items = await intercept_albertsons_ad(connect_url)
        
        job_state["status"] = "processing"  # <-- Phase 2 (will finish very quickly)
        if sanitized_items:
            store_id = await asyncio.to_thread(get_or_create_store, "Albertsons")
            await save_grocery_items(store_id, sanitized_items)
            
    finally:
        job_state["status"] = "idle" # <-- Phase 3
        print("Albertsons scraping job fully completed.")

async def run_scraping_pipeline(connect_url: str = None):
    try:
        job_state["status"] = "scraping"

        image_paths = await scrape_ad_images(connect_url)
        job_state["status"] = "processing"
        print("~~~~~~~~scrape success~~~~~~~")
        all_products = await extract_prices(image_paths)

        store_id = await asyncio.to_thread(get_or_create_store, "99 Ranch")
        await save_grocery_items(store_id, all_products)
    finally:
        # Guarantee we reset the state when done
        job_state["status"] = "idle"
        print("Background scraping job fully completed.")