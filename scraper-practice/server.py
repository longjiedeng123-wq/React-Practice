from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio


from services import job_state, run_scraping_pipeline, run_albertsons_pipeline

import os
from dotenv import load_dotenv
from supabase import create_client, Client

from pydantic import BaseModel
from typing import List, Optional
from google import genai

import json


load_dotenv()


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


@app.get("/")
def root():
    return {"Hello" : "world"}

@app.get("/api/prices")
async def get_grocery_prices(background_tasks: BackgroundTasks):
    
    print("API called: Starting scraping process...")
    session_id, connect_url, iframe_url = await create_live_session()

    background_tasks.add_task(run_scraping_pipeline, connect_url)

    
    return {
        "status": "success",
        "message": "Scraping started in the cloud.",
        "iframe_url": iframe_url,
        "session_id": session_id
    }

@app.get('/api/products')
def get_saved_products():
    products = get_all_products()

    return {
        "status": "success",
        "total_items": len(products),
        "data": products
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
        model='gemini-3.6-flash',
        contents=user_prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": AgentResponse,
        }
    )

    return json.loads(ai_response.text)




@app.get("/api/scrape-albertsons")
async def trigger_albertsons_scrape(background_tasks: BackgroundTasks):
    print("API called: Starting Albertsons scraping process...")
    session_id, connect_url, iframe_url = await create_live_session()
    
    # 2. Start the background task
    background_tasks.add_task(run_albertsons_pipeline, connect_url)
    
    # 3. Return the UI endpoints to React
    return {
        "status": "success",
        "message": "Albertsons scraping started in the cloud.",
        "iframe_url": iframe_url,
        "session_id": session_id
    }

@app.get("/api/status")
def get_scraping_status():
    return {"status": job_state["status"]}