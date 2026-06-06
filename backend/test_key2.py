import cohere
KEY = "your-api-key-here"
try:
    c = cohere.ClientV2(KEY)
    r = c.embed(texts=["test"], model="embed-english-v3.0", input_type="search_query")
    print(f"COHERE OK — dims: {len(r.embeddings[0])}")
except Exception as e:
    print(f"Cohere FAIL: {str(e)[:120]}")
