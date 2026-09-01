import os
import json
import asyncio
from dotenv import load_dotenv
from google import genai
from PIL import Image
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

client = genai.Client()

IMAGE_MODELS = [
    'gemini-3.7-flash',
    'gemini-3.6-flash',
    'gemini-3.5-flash',
    'gemini-2.5-flash'
]

class GroceryItemSchema(BaseModel):
    english_name: str = Field(description="The English name of the product.")
    chinese_name: Optional[str] = Field(None, description="The Chinese name. Null if missing.")
    original_price: Optional[float] = Field(None, description="Numerical original price.")
    discount_price: Optional[float] = Field(None, description="Numerical sale price.")
    unit: Optional[str] = Field(None, description="Base unit of sale (e.g., EA, PK, LB).")
    quantity: Optional[str] = Field(None, description="Size/weight/volume.")
    valid_dates: Optional[str] = Field(None, description="Date range valid for this item.")
    taxable: bool = Field(False, description="True ONLY if +TX is present.")
    has_crv: bool = Field(False, description="True ONLY if +CRV is present.")

    
async def extract_prices(image_paths):
    all_products = []
    print("Loading images...")

    prompt = """Extract the grocery products, their prices, and details from this weekly ad. 
    Apply the correct date range from the banners. 
    If the image contains NO specific grocery items, return an empty list."""

    
    for image_path in image_paths:
        ad_image = Image.open(image_path)
        success = False

        for model in IMAGE_MODELS:
            if success:
                break
            for attempt in range(1,4):
                try:
                    
                    print("AI searching...")
                    # response in json format
                    response = await client.aio.models.generate_content(
                        model=model,
                        contents=[prompt, ad_image],
                        config={
                            "response_mime_type": "application/json",
                            "response_schema": list[GroceryItemSchema]
                        }
                    ) 
                    

                    all_products.extend(json.loads(response.text))
                    
                    print("-------Each Response--------")
                    print(response.text)
                    success = True
                    await asyncio.sleep(4)
                    break
                except Exception as e:

                    error_msg = str(e).lower()
                    is_temporary = any(term in error_msg for term in ["503", "unavailable", "demand", "429", "quota", "exhausted"])
                    if is_temporary:
                        print(f"~~~~{model}: with {e}~~~~")
                        await asyncio.sleep(3 * attempt)
                    else:
                        print(f"Non-recoverable error on {model}: {e}")
                        break
        


    print("-------final product--------")
    print(all_products)
    return all_products