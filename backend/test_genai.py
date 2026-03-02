import sys
import os
sys.path.append('backend/venv/lib/python3.13/site-packages')
from google import genai
from google.genai import types

print(dir(types.GenerateContentConfig))
print("AUDIO" in dir(types))
