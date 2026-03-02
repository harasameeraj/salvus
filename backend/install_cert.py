import os
import ssl
import certifi
import sys

print("Installing certifi...")
os.system(f"{sys.prefix}/bin/pip install certifi")

try:
    print("Testing SSL context with certifi:")
    context = ssl.create_default_context(cafile=certifi.where())
    print("SUCCESS")
except Exception as e:
    print(e)
