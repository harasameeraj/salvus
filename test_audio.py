import asyncio
import os
import sys

# Load env variables from .env
from dotenv import load_dotenv
load_dotenv('.env')

from google import genai
from google.genai import types

async def test():
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    if not api_key:
        print("No API KEY!")
        return
        
    response = await client.aio.models.generate_content(
        model='gemini-2.5-flash',
        contents="Warning: Tornado detected in your area.",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Puck"
                    )
                )
            )
        ),
    )
    if hasattr(response.candidates[0].content.parts[0], 'inline_data'):
        print(f"Audio length: {len(response.candidates[0].content.parts[0].inline_data.data)}")
    else:
        print("No inline data.")
        print(response)

asyncio.run(test())
