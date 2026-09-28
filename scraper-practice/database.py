import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

def get_or_create_store(store_name: str) -> str:
    response = supabase.table("stores").select("id").eq("name", store_name).execute()

    if response.data:
        return response.data[0]["id"]

    new_store = supabase.table("stores").insert({"name": store_name}).execute()
    return new_store.data[0]["id"]