from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from scraper import scrape_ad_images
from ai_extractor import extract_prices

import os
from dotenv import load_dotenv
from supabase import create_client, Client

from pydantic import BaseModel
from typing import List, Optional
from google import genai

import json


load_dotenv()

url : str = os.environ.get("SUPABASE_URL", "")
key : str = os.environ.get("SUPABASE_KEY", "")
supabase : Client = create_client(url, key)

ai_client = genai.Client()
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

def get_or_create_store(store_name: str) -> str:
    response = supabase.table("stores").select("id").eq("name", store_name).execute()

    if response.data:
        return response.data[0]["id"] # type: ignore

    new_store = supabase.table("stores").insert({"name": store_name}).execute()
    return new_store.data[0]["id"] # type: ignore

async def save_grocery_items(store_id: str, extracted_items: list):
    valid_items = [item for item in extracted_items if item.get("english_name")]
    product_batch = []

    for item in valid_items:
        product_batch.append({
            "store_id": store_id,
            "english_name": item["english_name"],
            "chinese_name": item.get("chinese_name"),
            "base_unit_type": item.get("unit")
        }) 

    # 1. Define a synchronous wrapper for the product upsert
    def sync_upsert_products():
        return supabase.table("products").upsert(
            product_batch,
            on_conflict="store_id,english_name"
        ).execute()

    product_id_map = {}
    if product_batch:
        # 2. Await the wrapper in a background thread
        product_response = await asyncio.to_thread(sync_upsert_products)
        print(f"Upserted {len(product_response.data)} products.")
        
        product_id_map = {row["english_name"]: row["id"] for row in product_response.data} 

    price_batch = []
    for item in valid_items:
        english_name = item.get("english_name")
        
        if english_name not in product_id_map:
            continue
            
        price_batch.append({
            "product_id": product_id_map[english_name],
            "original_price": item.get("original_price"),
            "discount_price": item.get("discount_price"),
            "valid_dates": item.get("valid_dates"),
            "taxable": item.get("taxable"),
            "has_crv": item.get("has_crv")
        })

    # 3. Define a synchronous wrapper for the price insert
    def sync_insert_prices():
        return supabase.table("price_history").insert(price_batch).execute()

    if price_batch:
        # 4. Await the wrapper in a background thread
        price_response = await asyncio.to_thread(sync_insert_prices)
        print(f"Inserted {len(price_response.data)} price records.")


async def run_scraping_pipeline():
    image_paths = await scrape_ad_images()

    print("~~~~~~~~scrape success~~~~~~~")
    all_products = await extract_prices(image_paths)

    store_id = await asyncio.to_thread(get_or_create_store, "99 Ranch")
    await save_grocery_items(store_id, all_products)


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

class AgentItem(BaseModel):
    english_name: str
    discount_price: float
    original_price: Optional[float] = None
    unit: Optional[str] = None

class AgentResponse(BaseModel):
    conversational_message: str
    ui_items: List[AgentItem]



@app.post("/api/agent")
async def chat_with_grocery_agent(payload: dict):
    user_prompt = payload.get("user_prompt", "")
    print(f"Received user prompt: {user_prompt}")

    response = supabase.table("products").select(
        "english_name, base_unit_type, price_history(discount_price, original_price)"
    ).execute()

    catalog = json.dumps([{
        "name": p["english_name"],
        "unit": p["base_unit_type"],
        "price": p["price_history"][0].get("discount_price") if p.get("price_history") else None
    } for p in response.data])

    # 3. Inject the raw data into the system instruction
    system_instruction = f"""
    You are an expert grocery assistant and nutritionist.
    Here is the live grocery catalog with prices: {catalog}
    
    When the user asks a question, use your internal knowledge to calculate nutritional value (like protein per dollar) based strictly on these provided items.
    Provide a helpful conversational message summarizing your reasoning, and return the specific items they should buy.
    """

    # 4. Generate content without the tool
    ai_response = await ai_client.aio.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=user_prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": AgentResponse,
        }
    )

    return json.loads(ai_response.text)

