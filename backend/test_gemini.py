"""Direct Gemini API test — bypasses all backend layers."""
import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

key = "your-api-key-here"
base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

print(f"Key: {key[:20]}...")
print(f"Model: {model}")

client = OpenAI(api_key=key, base_url=base)

# Try current model first
for m in [model, "gemini-1.5-flash", "gemini-1.5-flash-8b"]:
    try:
        r = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
            max_tokens=5,
        )
        print(f"  {m}: OK — {r.choices[0].message.content!r}")
        break
    except Exception as e:
        code = getattr(e, 'status_code', '?')
        print(f"  {m}: {code} — {str(e)[:150]}")
