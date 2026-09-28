import os 
from contextlib import asynccontextmanager 
import asyncio
from browserbase import (
    AsyncBrowserbase,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)
from dotenv import load_dotenv 
from playwright.async_api import async_playwright 
load_dotenv()

MAX_RETRIES = 1
RETRY_DELAY = 3

@asynccontextmanager 
async def browser_session():  

    api_key = os.environ["BROWSERBASE_API_KEY"]     
    async with AsyncBrowserbase(api_key=api_key) as bb:  
        project_id = os.environ["BROWSERBASE_PROJECT_ID"]
        for attempt in range(MAX_RETRIES + 1):
            try:     
                session = await bb.sessions.create(project_id=project_id)
                async with async_playwright() as p:
                    browser = await p.chromium.connect_over_cdp(session.connect_url)
                    context = browser.contexts[0]
                    page = context.pages[0]
                    try:
                        await page.close()
                        await browser.close()
                    finally:
                        yield page
            except (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError) as e:
                if attempt < MAX_RETRIES:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY} seconds...")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    print(f"Attempt {attempt + 1} failed: {e}. No more retries left.")
                    raise

async def create_live_session():
    api_key = os.environ["BROWSERBASE_API_KEY"]
    project_id = os.environ["BROWSERBASE_PROJECT_ID"]
    
    async with AsyncBrowserbase(api_key=api_key) as bb:
        # 1. Boot up a fresh headless Chromium browser in the cloud
        session = await bb.sessions.create(project_id=project_id)
        
        # 2. Ask Browserbase for the live debugging URLs for this specific session
        live_view_links = await bb.sessions.debug(session.id)
        
        # 3. Extract the fullscreen URL and hide the built-in navbar for a cleaner UI
        clean_iframe_url = f"{live_view_links.debuggerFullscreenUrl}&navbar=false"
        
        # 4. Return the necessary connection details
        return session.id, session.connect_url, clean_iframe_url