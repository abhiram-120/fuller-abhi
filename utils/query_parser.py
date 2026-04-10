import json

from utils.gemini_llm import api_key, generate_json_text

SYSTEM = "You extract structured intent from user queries. Return only valid JSON as specified."


def parse_query(query):
    if not api_key():
        return None

    prompt = f"""Extract structured intent from this nonprofit targeting query.
Return JSON only with these keys:
- sector: the type of nonprofit or cause area (e.g. "hunger relief", "education", "environment")
- signal: what buying signal to look for (e.g. "hiring fundraising director", "launching campaign", "received grant")
- location: city or state if mentioned, otherwise null

If the query is too vague to extract any sector or signal, return JSON null (the literal null value, not a string).

Query: {query}"""

    try:
        raw = generate_json_text(SYSTEM, prompt, max_output_tokens=1024)
        if raw is None:
            return None
        if raw.lower() == "null":
            return None
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip()
        parsed = json.loads(raw)
        if parsed is None:
            return None
        return parsed
    except Exception:
        return None
