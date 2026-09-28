from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware


from ai_agent import ask_grocery_agent
from database import  get_all_products
from services import job_state, run_scraping_pipeline, run_albertsons_pipeline
from browser_session import create_live_session

import os
from dotenv import load_dotenv



load_dotenv()


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



@app.post("/api/agent")
async def chat_with_grocery_agent(payload: dict):
    user_prompt = payload.get("user_prompt", "")
    print(f"Received user prompt: {user_prompt}")

    response_data = await ask_grocery_agent(user_prompt)

    return response_data




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