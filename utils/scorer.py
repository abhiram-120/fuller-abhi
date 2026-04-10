import json

from utils.gemini_llm import api_key, generate_json_text

SYSTEM = """You are a nonprofit buying signal analyst for a sales intelligence platform.
You receive nonprofits with financial data, hiring activity, and news signals.
Return a ranked JSON array based on how likely each org is to hire an external agency right now.

Rules:
- Score 0 to 100 based only on signals actually present. Do not invent signals.
- Set data_quality to "strong" if all three signals have real content, "moderate" if two do, "weak" if one or none.
- If signals contradict each other (e.g. revenue declining but hiring senior staff), set mixed_signal to true and explain both interpretations in reasoning.
- For weak data_quality orgs, score conservatively.
- Return only valid JSON array, no text outside it.
- Each object must have: name, score, data_quality, mixed_signal, financial_signal, hiring_signal, news_signal, reasoning, outreach_subject, outreach_email"""


def score_orgs(query, intent, orgs):
    if not api_key():
        return None

    orgs_text = json.dumps([{
        "name": o["name"],
        "city": o.get("city"),
        "state": o.get("state"),
        "revenue": o.get("revenue"),
        "revenue_trend": o.get("revenue_trend"),
        "hiring": o.get("hiring") or "No data found",
        "news": o.get("news") or "No data found"
    } for o in orgs], indent=2)

    prompt = f"""Query: {query}
Intent extracted: {json.dumps(intent)}

Nonprofits to analyse:
{orgs_text}

Reflect missing data honestly. Flag contradictory signals. Return JSON array ranked by score descending.
Outreach email must reference only confirmed signals, 3 sentences max."""

    try:
        raw = generate_json_text(SYSTEM, prompt, max_output_tokens=32768)
        if raw is None:
            return None
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Scoring failed: {e}")
        return None
