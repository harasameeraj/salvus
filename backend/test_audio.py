import asyncio
import os
import aiohttp
import base64
import ssl
import certifi

from dotenv import load_dotenv
load_dotenv('.env')

async def test():
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1alpha/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    
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
    
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, ssl=ssl_context) as response:
            result = await response.json()
            if "candidates" in result:
                parts = result["candidates"][0]["content"]["parts"]
                for p in parts:
                    if "inlineData" in p and p["inlineData"]["mimeType"].startswith("audio"):
                        audio_b64 = p["inlineData"]["data"]
                        audio_bytes = base64.b64decode(audio_b64)
                        print(f"SUCCESS: Audio generated, {len(audio_bytes)} bytes")
                        return
            print("FAILED")
            print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test())
