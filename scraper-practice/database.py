import os
from dotenv import load_dotenv
import asyncio
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

def get_or_create_store(store_name: str) -> str:
    response = supabase.table("stores").select("id").eq("name", store_name).execute()

    if response.data:
        return response.data[0]["id"]

    new_store = supabase.table("stores").insert({"name": store_name}).execute()
    return new_store.data[0]["id"]

async def save_grocery_items(store_id: str, extracted_items: list):

    unique_products = {}
    for item in extracted_items:
        name = item.get("english_name")
        if name:
            unique_products[name] = item

    valid_items = list(unique_products.values())
    
    product_batch = []

    for item in valid_items:
        product_batch.append({
            "store_id": store_id,
            "english_name": item["english_name"],
            "chinese_name": item.get("chinese_name"),
            "base_unit_type": item.get("base_unit_type") or item.get("unit")
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
            "taxable": item.get("taxable", False),
            "has_crv": item.get("has_crv", False),
            "min_qty_required": item.get("min_qty_required", 1),
            "limit_qty": item.get("limit_qty")
        })

    # 3. Define a synchronous wrapper for the price insert
    def sync_insert_prices():
        return supabase.table("price_history").insert(price_batch).execute()

    if price_batch:
        # 4. Await the wrapper in a background thread
        price_response = await asyncio.to_thread(sync_insert_prices)
        print(f"Inserted {len(price_response.data)} price records.")


def get_all_products() -> list:
    response = supabase.table("products").select(
        "english_name, chinese_name, base_unit_type, price_history(original_price, discount_price, valid_dates, taxable, has_crv)"
    ).execute()

    formatted_products = []
    for product in response.data:
        p: dict = product 
        history: list = p.get("price_history", [])

        latest_price: dict = history[0] if history else {}

        formatted_products.append({
            "english_name": p.get("english_name"),
            "chinese_name": p.get("chinese_name"),
            "unit": p.get("base_unit_type"),
            "original_price": latest_price.get("original_price"),
            "discount_price": latest_price.get("discount_price"),
            "taxable": latest_price.get("taxable"),
            "has_crv": latest_price.get("has_crv")
        })

    return formatted_products