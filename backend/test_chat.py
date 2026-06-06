"""Quick end-to-end smoke test: health + chat."""
import json
import sys
import urllib.request

BASE = "http://localhost:8000"

# 1. Health
r = urllib.request.urlopen(f"{BASE}/health")
print(f"Health: {r.status}", json.loads(r.read())["status"])

# 2. Verify collection
r = urllib.request.urlopen(f"{BASE}/api/v1/verify")
info = json.loads(r.read())
print(f"Collection: {info}")

# 3. Chat
payload = json.dumps({
    "question": "What is Physical AI and how does it relate to humanoid robotics?",
    "top_k": 10
}).encode()

req = urllib.request.Request(
    f"{BASE}/api/v1/chat",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
r = urllib.request.urlopen(req, timeout=60)
resp = json.loads(r.read())
print(f"\nChat response (status {r.status}):")
print(resp.get("answer", resp)[:800])
print(f"\nConfidence: {resp.get('confidence')}")
print(f"Sources: {len(resp.get('sources', []))}")
