import json
from datetime import datetime

def score_color(score):
    if score >= 75:
        return "#4ade80"
    if score >= 50:
        return "#facc15"
    return "#f87171"

def signal_pill(label, text):
    if not text or "no data" in text.lower() or "no signal" in text.lower():
        return f'<span class="pill pill-off">{label}: none</span>'
    return f'<span class="pill pill-on">{label}</span>'

def quality_badge(quality):
    colors = {"strong": "#4ade80", "moderate": "#facc15", "weak": "#f87171"}
    color = colors.get(quality, "#555")
    return f'<span class="quality-badge" style="border-color:{color};color:{color}">data: {quality or "unknown"}</span>'

def mixed_badge(mixed):
    if not mixed:
        return ""
    return '<span class="mixed-badge">mixed signals</span>'

def org_card(org, index):
    contact = org.get("contact") or {}
    score = org.get("score", 0)
    color = score_color(score)

    if contact.get("email"):
        confidence_color = "#4ade80" if contact.get("confidence") == "verified" else "#facc15"
        contact_html = f"""<div class="contact">
            <span class="contact-name">{contact.get('name', '')} <span class="contact-title">{contact.get('title', '')}</span></span>
            <span class="contact-email">{contact['email']} <span class="badge" style="color:{confidence_color}">{contact.get('confidence')}</span></span>
        </div>"""
    else:
        contact_html = '<div class="contact contact-missing">Contact not found</div>'

    return f"""<div class="card">
        <div class="card-header">
            <div>
                <div class="org-name">{index + 1}. {org.get('name', 'Unknown')}</div>
                <div class="org-location">{org.get('city', '')}{', ' + org.get('state', '') if org.get('state') else ''} {quality_badge(org.get('data_quality'))} {mixed_badge(org.get('mixed_signal'))}</div>
            </div>
            <div class="score-badge" style="color:{color}">{score}</div>
        </div>
        <div class="pills">
            {signal_pill("Revenue", org.get('financial_signal'))}
            {signal_pill("Hiring", org.get('hiring_signal'))}
            {signal_pill("Activity", org.get('news_signal'))}
        </div>
        <div class="signals">
            <div class="signal-row"><span class="signal-label">Financial</span><span>{org.get('financial_signal', 'No signal found')}</span></div>
            <div class="signal-row"><span class="signal-label">Hiring</span><span>{org.get('hiring_signal', 'No signal found')}</span></div>
            <div class="signal-row"><span class="signal-label">Activity</span><span>{org.get('news_signal', 'No signal found')}</span></div>
        </div>
        <div class="reasoning">{org.get('reasoning', '')}</div>
        {contact_html}
        <div class="email-section">
            <div class="email-subject">Subject: {org.get('outreach_subject', '')}</div>
            <div class="email-body" id="email-{index}">{org.get('outreach_email', '')}</div>
            <button class="copy-btn" onclick="copyEmail({index}, this)">Copy email</button>
        </div>
    </div>"""

def generate_report(query, orgs, output_path):
    cards = "".join(org_card(org, i) for i, org in enumerate(orgs))
    timestamp = datetime.now().strftime("%d %b %Y %H:%M")

    csv_data = []
    for org in orgs:
        contact = org.get("contact") or {}
        csv_data.append({
            "name": org.get("name", ""),
            "score": org.get("score", ""),
            "data_quality": org.get("data_quality", ""),
            "mixed_signal": org.get("mixed_signal", False),
            "email": contact.get("email", ""),
            "confidence": contact.get("confidence", ""),
            "reasoning": org.get("reasoning", "")
        })

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fuller Focus Signal Report</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0a0a0a; color: #e5e5e5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; line-height: 1.6; padding: 40px 20px; }}
  .container {{ max-width: 860px; margin: 0 auto; }}
  .header {{ margin-bottom: 40px; border-bottom: 1px solid #1f1f1f; padding-bottom: 24px; }}
  .header-top {{ display: flex; justify-content: space-between; align-items: flex-start; }}
  .brand {{ font-size: 12px; color: #555; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 8px; }}
  .query-text {{ font-size: 20px; color: #fff; font-weight: 500; }}
  .meta {{ font-size: 12px; color: #555; margin-top: 8px; }}
  .export-btn {{ background: #1f1f1f; color: #aaa; border: 1px solid #2a2a2a; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 12px; }}
  .export-btn:hover {{ background: #2a2a2a; color: #fff; }}
  .card {{ background: #111; border: 1px solid #1f1f1f; border-radius: 10px; padding: 24px; margin-bottom: 16px; }}
  .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
  .org-name {{ font-size: 16px; font-weight: 600; color: #fff; }}
  .org-location {{ font-size: 12px; color: #555; margin-top: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .score-badge {{ font-size: 32px; font-weight: 700; }}
  .quality-badge {{ font-size: 11px; padding: 1px 7px; border-radius: 4px; border: 1px solid; }}
  .mixed-badge {{ font-size: 11px; padding: 1px 7px; border-radius: 4px; border: 1px solid #7c3aed; color: #a78bfa; }}
  .pills {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
  .pill {{ font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 500; }}
  .pill-on {{ background: #1a2a1a; color: #4ade80; border: 1px solid #2a3a2a; }}
  .pill-off {{ background: #1a1a1a; color: #555; border: 1px solid #222; }}
  .signals {{ display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }}
  .signal-row {{ display: flex; gap: 12px; font-size: 13px; }}
  .signal-label {{ color: #555; width: 70px; flex-shrink: 0; }}
  .reasoning {{ font-size: 13px; color: #999; border-left: 2px solid #1f1f1f; padding-left: 12px; margin-bottom: 16px; }}
  .contact {{ font-size: 13px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 2px; }}
  .contact-name {{ color: #ccc; }}
  .contact-title {{ color: #555; font-size: 12px; }}
  .contact-email {{ color: #aaa; }}
  .contact-missing {{ color: #444; }}
  .badge {{ font-size: 11px; padding: 1px 6px; border-radius: 4px; background: #111; }}
  .email-section {{ background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 6px; padding: 16px; }}
  .email-subject {{ font-size: 12px; color: #555; margin-bottom: 8px; }}
  .email-body {{ font-size: 13px; color: #aaa; white-space: pre-wrap; margin-bottom: 12px; }}
  .copy-btn {{ background: #1f1f1f; color: #aaa; border: 1px solid #2a2a2a; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
  .copy-btn:hover {{ background: #2a2a2a; color: #fff; }}
  .copy-btn.copied {{ color: #4ade80; border-color: #2a3a2a; }}
  .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a1a1a; font-size: 11px; color: #333; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="header-top">
      <div>
        <div class="brand">Fuller Focus Signal Agent</div>
        <div class="query-text">"{query}"</div>
        <div class="meta">{len(orgs)} organisations found - {timestamp}</div>
      </div>
      <button class="export-btn" onclick="exportCSV()">Export CSV</button>
    </div>
  </div>
  {cards}
  <div class="footer">Fuller Focus Signal Agent v1</div>
</div>
<script>
function copyEmail(index, btn) {{
  const el = document.getElementById('email-' + index);
  navigator.clipboard.writeText(el.innerText).then(() => {{
    btn.textContent = 'Copied';
    btn.classList.add('copied');
    setTimeout(() => {{ btn.textContent = 'Copy email'; btn.classList.remove('copied'); }}, 2000);
  }});
}}

const csvData = {json.dumps(csv_data)};

function exportCSV() {{
  const headers = ['Name', 'Score', 'Data Quality', 'Mixed Signal', 'Email', 'Confidence', 'Reasoning'];
  const rows = csvData.map(r => [r.name, r.score, r.data_quality, r.mixed_signal, r.email, r.confidence, r.reasoning].map(v => '"' + String(v === null || v === undefined ? '' : v).replace(/"/g, '""') + '"').join(','));
  const csv = [headers.join(','), ...rows].join('\\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = 'fuller-focus-signals.csv';
  a.click();
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
