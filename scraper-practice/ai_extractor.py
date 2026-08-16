import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client()

model_id = 'gemini-3.5-flash'

print("Loading image...")
count = 1
image_path = f"weekly_ad_{count}.jpg"
ad_image = Image.open(image_path)

prompt = """You are a data extraction bot. Look at this grocery store weekly ad. 
Extract the products and their prices. 
Return ONLY a valid JSON list of objects. 
Each object must have exactly these keys: "item_name", "price", and "unit".
Do not include any extra text, explanations, or markdown formatting. Just the raw JSON."""

print("AI searching...")
response = client.models.generate_content(
    model=model_id,
    contents=[prompt, ad_image]
)

print("-------AI RESULT-----")
print(response.text)