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
    prompt = """You are a highly precise data extraction bot analyzing grocery store weekly ads. 
    Extract the products, their prices, and their associated details. 
    
    CRITICAL INSTRUCTIONS FOR CONTEXT:
    1. Observe date headers (e.g., "08/07/26 - 08/20/26" or "08/14/26 - 08/20/26"). Apply the correct date range to the items directly below that specific banner.
    2. Identify the package quantity usually found in the top left or near the item (e.g., "25lb", "3L", "400g", "1.15kg").
    3. Identify if there is an original price (usually crossed out or printed smaller) and a discount/sale price (usually larger and more prominent).
    4. If the image is a general flyer containing NO specific grocery items or prices, return an empty JSON array: []
    
    Return ONLY a valid JSON list of objects. Do not include any markdown formatting or extra text.
    
    Each object must have exactly these keys:
    - "english_name": The English name of the product.
    - "chinese_name": The Chinese name of the product. Return null if missing.
    - "original_price": The numerical original price before any discount (e.g., "8.99"). Return null if there is no distinct original price shown.
    - "discount_price": The numerical sale price (e.g., "6.99"). If only one price is shown on the item, use it here.
    - "unit": The base unit of sale (e.g., "EA", "PK", "LB"). DO NOT include TX or CRV here. Return null if missing.
    - "quantity": The size/weight/volume of the item (e.g., "25lb", "3L", "400g"). Return null if missing.
    - "valid_dates": The date range valid for this item. Return null if missing.
    - "taxable": Boolean (true or false). Set to true ONLY if "+TX" is present near the price/unit.
    - "has_crv": Boolean (true or false). Set to true ONLY if "+CRV" is present near the price/unit.

    If any string attribute is missing from the image for a specific item, return the JSON value `null` (not the string "null")."""

    for image_path in image_paths:
        try:
            ad_image = Image.open(image_path)

            print("AI searching...")
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt, ad_image]
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()

            all_products.extend(json.loads(clean_text))
            
            print("-------Each Response--------")
            print(response.text)
        except Exception as e:
            print("Failure with Error: {e}")
    print("-------final product--------")
    print(all_products)
    return all_products