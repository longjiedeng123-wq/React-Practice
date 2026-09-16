import os 
from contextlib import asynccontextmanager 
from browserbase import AsyncBrowserbase 
from dotenv import load_dotenv 
from playwright.async_api import async_playwright 
load_dotenv()

@asynccontextmanager 
async def browser_session():     
    api_key = os.environ["BROWSERBASE_API_KEY"]     
    bb = AsyncBrowserbase(api_key=api_key)     
    project_id = os.environ["BROWSERBASE_PROJECT_ID"]     
    session = await bb.sessions.create(project_id=project_id)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]

        try:
            yield page
        finally:
            await page.close()
            await browser.close()