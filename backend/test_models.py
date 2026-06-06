"""Try every available Gemini model to find one with quota remaining."""
import os, sys
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

key = os.getenv("GEMINI_API_KEY")
base = "https://generativelanguage.googleapis.com/v1beta/openai/"

client = OpenAI(api_key=key, base_url=base)

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash-8b-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
]

working = None
for m in MODELS:
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Reply OK"}],
            max_tokens=5,
        )
        print(f"  WORKS: {m} -> {r.choices[0].message.content!r}")
        working = m
        break
    except Exception as e:
        code = getattr(e, 'status_code', '?')
        msg = str(e)[:80]
        print(f"  {code}  {m}: {msg}")

if working:
    print(f"\nUSE MODEL: {working}")
else:
    print("\nNo Gemini model has quota — need Groq or billing")
