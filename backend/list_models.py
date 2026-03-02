import asyncio
import os
from google import genai
from dotenv import load_dotenv

load_dotenv('.env')
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

for m in client.models.list():
    if "models/gemini-2.0-flash-exp" in m.name or "models/gemini-2.0-flash-lite-preview-02-05" in m.name or "models/gemini-2.5" in m.name:
         print(f"Model: {m.name}")
