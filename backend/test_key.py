"""Identify which service the pasted key belongs to."""
import sys

KEY = "your-api-key-here"

# --- Try Cohere ---
try:
    import cohere
    c = cohere.ClientV2(KEY)
    r = c.embed(texts=["test"], model="embed-english-v3.0", input_type="search_query")
    print(f"COHERE OK — dims: {len(r.embeddings[0])}")
except Exception as e:
    print(f"Cohere FAIL: {type(e).__name__}: {str(e)[:120]}")

# --- Try Gemini via OpenAI-compat ---
try:
    from openai import OpenAI
    client = OpenAI(
        api_key=KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    resp = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[{"role": "user", "content": "say hi"}],
        max_tokens=10,
    )
    print(f"GEMINI OK — {resp.choices[0].message.content!r}")
except Exception as e:
    print(f"Gemini FAIL: {type(e).__name__}: {str(e)[:120]}")
