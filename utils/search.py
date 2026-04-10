import os
import time
import requests

TAVILY_URL = "https://api.tavily.com/search"

def search(query):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return []

    for attempt in range(3):
        try:
            resp = requests.post(
                TAVILY_URL,
                json={"api_key": key, "query": query, "max_results": 3},
                timeout=10
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return [r.get("content", "") for r in resp.json().get("results", [])]
        except Exception:
            if attempt == 2:
                return []
            time.sleep(1)
    return []

def hiring_signals(org_name, signal_hint=""):
    base = signal_hint or "fundraising marketing development director"
    results = search(f"{org_name} hiring {base} 2025 2026")
    return " ".join(results)[:600] if results else ""

def news_signals(org_name):
    results = search(f"{org_name} campaign launch initiative grant announcement 2025 2026")
    return " ".join(results)[:600] if results else ""
