import asyncio
import os
import aiohttp
import base64
import ssl
import certifi

from dotenv import load_dotenv
load_dotenv('.env')

async def test_model(model_name, api_key, session, ssl_context):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": "Evacuate immediately. A hurricane is approaching."}]
        }],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Puck"
                    }
                }
            }
        }
    }
    
    async with session.post(url, json=payload, ssl=ssl_context) as response:
        result = await response.json()
        if "candidates" in result:
            parts = result["candidates"][0]["content"]["parts"]
            for p in parts:
                if "inlineData" in p and p["inlineData"]["mimeType"].startswith("audio"):
                    audio_b64 = p["inlineData"]["data"]
                    audio_bytes = base64.b64decode(audio_b64)
                    print(f"[{model_name}] SUCCESS: Audio generated, {len(audio_bytes)} bytes")
                    return True
        print(f"[{model_name}] FAILED: {result.get('error', {}).get('message', 'Unknown error')}")
        return False

async def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    models_to_test = [
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-flash-native-audio-latest",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    async with aiohttp.ClientSession() as session:
        for m in models_to_test:
            await test_model(m, api_key, session, ssl_context)

if __name__ == "__main__":
    asyncio.run(main())
