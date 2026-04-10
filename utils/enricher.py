import os
import re
import time
import requests

def enrich_contact(org_name):
    domain = find_real_domain(org_name)
    if domain:
        result = hunter_lookup(domain)
        if result:
            return result
    return {"name": "", "email": "", "title": "", "confidence": "not found"}

def find_real_domain(org_name):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        return None
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": f"{org_name} official website", "max_results": 1},
                timeout=10
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                return None
            url = results[0].get("url", "")
            match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            return match.group(1) if match else None
        except Exception:
            if attempt == 2:
                return None
            time.sleep(1)
    return None

def hunter_lookup(domain):
    key = os.getenv("HUNTER_API_KEY")
    if not key:
        return None
    try:
        resp = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": key, "limit": 1},
            timeout=10
        )
        resp.raise_for_status()
        emails = resp.json().get("data", {}).get("emails", [])
        if not emails:
            return None
        top = emails[0]
        return {
            "name": f"{top.get('first_name', '')} {top.get('last_name', '')}".strip(),
            "email": top.get("value"),
            "title": top.get("position", ""),
            "confidence": "verified" if top.get("confidence", 0) > 70 else "likely"
        }
    except Exception:
        return None
