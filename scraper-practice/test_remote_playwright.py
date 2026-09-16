import os
from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import asyncio

load_dotenv()

api_key = os.environ["BROWSERBASE_API_KEY"]
bb = Browserbase(api_key=api_key)





async def main():
    project_id = os.environ["BROWSERBASE_PROJECT_ID"]
    session = bb.sessions.create(project_id=project_id)
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(session.connect_url)

asyncio.run(main())