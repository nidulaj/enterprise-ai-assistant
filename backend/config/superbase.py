import os
from dotenv import load_dotenv
from superbase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

superbase = create_client(url, key)