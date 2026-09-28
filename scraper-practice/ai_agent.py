import json
from google import genai
from pydantic import BaseModel
from typing import List, Optional

# The AI service should fetch its own data
from database import get_agent_catalog

ai_client = genai.Client()

class AgentItem(BaseModel):
    english_name: str
    discount_price: float
    original_price: Optional[float] = None
    unit: Optional[str] = None

class AgentResponse(BaseModel):
    conversational_message: str
    ui_items: List[AgentItem]

async def ask_grocery_agent(user_prompt: str) -> dict:
    # 1. Get data
    catalog = get_agent_catalog()

    # 2. Build prompt
    system_instruction = f"""
    You are an expert grocery assistant and nutritionist.
    Here is the live grocery catalog with prices: {catalog}
    
    When the user asks a question, use your internal knowledge to calculate nutritional value (like protein per dollar) based strictly on these provided items.
    Provide a helpful conversational message summarizing your reasoning, and return the specific items they should buy.
    """

    # 3. Call Gemini
    ai_response = await ai_client.aio.models.generate_content(
        model='gemini-3.6-flash',
        contents=user_prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": AgentResponse,
        }
    )

    return json.loads(ai_response.text)