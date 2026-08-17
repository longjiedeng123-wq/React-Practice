import os
import json
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client()

model_id = 'gemini-3.5-flash'

def extract_prices(image_paths):
    all_products = []
    print("Loading images...")
    prompt = """You are a data extraction bot. Look at this grocery store weekly ad. 
                Extract the products and their prices. 
                Return ONLY a valid JSON list of objects. 
                Each object must have exactly these keys: "item_name", "price", "unit" and "quantities".
                Do not include any extra text, explanations, or markdown formatting. Just the raw JSON."""
    for image_path in image_paths:
        try:
            ad_image = Image.open(image_path)

            print("AI searching...")
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt, ad_image]
            )

            all_products.append(json.loads(response.text))
            print("-------Each Response--------")
            print(response.text)
        except Exception as e:
            print("Failure with Error: {e}")
    print("-------final product--------")
    print(all_products)
    return all_products