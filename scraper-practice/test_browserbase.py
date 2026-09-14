import os
from browserbase import Browserbase
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["BROWSERBASE_API_KEY"]
bb = Browserbase(api_key=api_key)
