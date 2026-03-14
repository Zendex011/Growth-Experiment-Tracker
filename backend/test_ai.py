import os
from dotenv import load_dotenv
from groq import Groq
import time

load_dotenv()

key = os.environ.get("GROQ_API_KEY", "")
print(f"Groq key: {key[:8]}..." if key else "GROQ_API_KEY not set!")

if not key:
    exit(1)

print("Sending request to Groq...")

start = time.time()

client = Groq(api_key=key)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Reply with this exact JSON and nothing else: {\"message\": \"hello\", \"status\": \"working\"}"}],
    max_tokens=50,
    temperature=0,
)

elapsed = time.time() - start
print(f"Response in {elapsed:.1f}s")
print(f"Raw output: {response.choices[0].message.content}")