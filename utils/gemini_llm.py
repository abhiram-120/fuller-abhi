import os
import re
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai


def api_key():
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def model_name():
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _is_rate_limit_error(err):
    msg = str(err).lower()
    return (
        "429" in msg
        or "resource exhausted" in msg
        or ("quota" in msg and "exceed" in msg)
    )


def generate_json_text(system_instruction, user_prompt, max_output_tokens=8192):
    """
    Call Gemini with JSON output. Returns raw text (JSON) or None on failure.
    Retries on rate limits (429 / quota) with backoff — common on free tier.
    """
    key = api_key()
    if not key:
        return None
    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        model_name(),
        system_instruction=system_instruction or None,
    )
    last_err = None
    for attempt in range(4):
        try:
            resp = model.generate_content(
                user_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": max_output_tokens,
                },
            )
            if not resp.candidates:
                return None
            return (resp.text or "").strip()
        except Exception as e:
            last_err = e
            if _is_rate_limit_error(e) and attempt < 3:
                delay = 15 * (2 ** attempt)
                m = re.search(r"retry in ([\d.]+)s", str(e), re.I)
                if m:
                    delay = max(delay, float(m.group(1)) + 2)
                print(f"Gemini rate limited; retrying in {delay:.0f}s...")
                time.sleep(delay)
                continue
            print(f"Gemini request failed: {e}")
            return None
    print(f"Gemini request failed after retries: {last_err}")
    return None
