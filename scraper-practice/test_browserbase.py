import os
from browserbase import Browserbase
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["BROWSERBASE_API_KEY"]
bb = Browserbase(api_key=api_key)

project_id = os.environ["BROWSERBASE_PROJECT_ID"]
session = bb.sessions.create(project_id=project_id)

print(f"Session created: {session.id}")