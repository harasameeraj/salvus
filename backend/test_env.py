import os
from dotenv import load_dotenv
load_dotenv()
print("KEY:", os.environ.get("GEMINI_API_KEY"))
