import time
import requests

BASE = "https://projects.propublica.org/nonprofits/api/v2"

def get_with_retry(url, params=None):
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1.5 ** attempt)

def get_nonprofits(query, limit=10):
    # ProPublica returns HTTP 404 when there are zero matches (JSON body is still valid).
    orgs = []
    for attempt in range(3):
        try:
            resp = requests.get(f"{BASE}/search.json", params={"q": query}, timeout=10)
            if resp.status_code in (200, 404):
                orgs = resp.json().get("organizations", [])[:limit]
                break
            resp.raise_for_status()
        except Exception:
            if attempt == 2:
                orgs = []
            else:
                time.sleep(1.5 ** attempt)
    results = []
    for org in orgs:
        detail = get_financials(org.get("ein"))
        results.append({
            "name": org.get("name"),
            "city": org.get("city"),
            "state": org.get("state"),
            "ein": org.get("ein"),
            "revenue": detail.get("revenue"),
            "revenue_trend": detail.get("trend"),
            "ntee_code": org.get("ntee_code")
        })
    return results

def get_financials(ein):
    if not ein:
        return {"revenue": None, "trend": "unknown"}
    try:
        resp = get_with_retry(f"{BASE}/organizations/{ein}.json")
        filings = resp.json().get("filings_with_data", [])[:3]
        if not filings:
            return {"revenue": None, "trend": "unknown"}
        revenues = [f.get("totrevenue", 0) for f in filings if f.get("totrevenue")]
        if len(revenues) >= 2:
            trend = "growing" if revenues[0] > revenues[-1] else "declining"
        else:
            trend = "stable"
        return {"revenue": revenues[0] if revenues else None, "trend": trend}
    except Exception:
        return {"revenue": None, "trend": "unknown"}
