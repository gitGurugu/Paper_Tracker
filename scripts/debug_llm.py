"""Local diagnostic for the LLM relay.

Run this from a machine where the relay works (e.g. your own PC / the same
network ccswitch uses) to see exactly *why* GitHub Actions gets
"Your request was blocked." It sends the same chat-completions request the
analyzer sends and dumps the raw HTTP status, headers, and body so we can tell
whether it's a Cloudflare/WAF block, an auth issue, a bad model, etc.

Usage (bash):
  LLM_API_KEY=xxx LLM_BASE_URL=https://app.bmw888.asia/v1 LLM_MODEL=gpt-5.5 \
    python scripts/debug_llm.py

Or put those three in a .env file in the project root and just run:
  python scripts/debug_llm.py
"""

import json
import os

import httpx

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

base_url = os.getenv("LLM_BASE_URL", "").rstrip("/")
api_key = os.getenv("LLM_API_KEY", "")
model = os.getenv("LLM_MODEL", "")

if not (base_url and api_key and model):
    raise SystemExit(
        "Set LLM_API_KEY, LLM_BASE_URL, LLM_MODEL (env vars or .env) first."
    )

masked = (api_key[:6] + "..." + api_key[-4:]) if len(api_key) > 12 else "***"
print(f"base_url = {base_url}")
print(f"model    = {model}")
print(f"api_key  = {masked}")
print("=" * 60)

url = f"{base_url}/responses"
payload = {
    "model": model,
    "input": "ping, reply with one word: pong",
    "max_output_tokens": 64,
}
base_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

# Headers worth inspecting to identify the blocker (Cloudflare etc.).
INTERESTING = [
    "server",
    "cf-ray",
    "cf-mitigated",
    "cf-cache-status",
    "content-type",
    "x-request-id",
    "retry-after",
    "www-authenticate",
]


def _extract_output_text(data: dict) -> str:
    """Pull the assistant text out of a Responses API payload."""
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    chunks = []
    for item in data.get("output") or []:
        for part in item.get("content") or []:
            if isinstance(part.get("text"), str):
                chunks.append(part["text"])
    return "".join(chunks)


def show(title: str, resp: httpx.Response) -> None:
    print(f"\n### {title}")
    print(f"HTTP {resp.status_code} {resp.reason_phrase}")
    for h in INTERESTING:
        if h in resp.headers:
            print(f"  {h}: {resp.headers[h]}")

    body = resp.text
    try:
        data = json.loads(body)
    except Exception:
        data = None

    if isinstance(data, dict):
        # The actual model that served the request (may differ from requested).
        print(f"  requested model : {model}")
        print(f"  responded model : {data.get('model', '(not reported)')}")
        if data.get("status"):
            print(f"  status          : {data.get('status')}")
        answer = _extract_output_text(data)
        if answer:
            print(f"--- assistant output text ---\n{answer[:500]}")

    print("--- raw body (first 1500 chars) ---")
    print(body[:1500])


def attempt(title: str, headers: dict) -> None:
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as c:
            resp = c.post(url, json=payload, headers=headers)
            show(title, resp)
    except Exception as e:  # noqa: BLE001 - we want to see everything
        print(f"\n### {title}\nRequest raised: {type(e).__name__}: {e}")


# 1) Exactly like the analyzer (plain python/httpx client).
attempt("Default request (like the analyzer)", base_headers)

# 2) With a browser-like User-Agent — tells us if a WAF is filtering on UA.
browser_headers = dict(base_headers)
browser_headers["User-Agent"] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
attempt("With browser User-Agent", browser_headers)

print("\n" + "=" * 60)
print("Read-out guide (testing the /responses endpoint):")
print("  - HTTP 200 + JSON containing 'output'/'pong' -> Responses API works.")
print("  - 503 'Service temporarily unavailable'      -> upstream/model issue, retry or check model.")
print("  - 404 'not found'                            -> endpoint path wrong.")
print("  - 401 'invalid api key'                      -> key/base_url mismatch.")
print("  - JSON 'model ... not found'                 -> fix LLM_MODEL (try 'gpt-5.5').")
