Fuller Focus Signal Agent

During our call you described two problems that stuck with me : buying signals not being insightful enough,
and nonprofit contact data being outdated. This agent was built around both.

Before reading anything else, open example_output/example_report.html in your browser.

---

PROBLEM STATEMENT

Agencies that sell services to nonprofits have no systematic way to know which orgs are
ready to buy right now. They cold outreach everyone or manually research one org at a time.
Both are slow and mostly guesswork.

On top of that, even when they find a warm target, the contact data is wrong. Emails
bounce. Decision makers have changed. This agent solves both problems from one query.

---

VALUE

One closed deal from a nonprofit is worth $5,000 to $100,000+ depending on the service.
If this agent surfaces 10 warm leads instead of 100 cold ones, conversion rate changes
significantly. For Fuller Focus, this becomes a product feature customers pay for.
Instead of a static database, they get a live signal engine that updates every run.

Cost per run is approximately $0.15. At 100 runs per day that is under $600 per month.
Profitable inside any subscription above $99 per month.

---

WHY THIS APPROACH

Option 3 was chosen because it directly addresses what was described in our call:
signals not being insightful enough. The agent does not just return data. It explains
which orgs matter right now and why, using three real-time signal sources.

Option 1 (RFP) was considered and dropped. RFPs are rare. A nonprofit issues maybe two
per year. That is a thin signal. Option 3 gives continuous signals because hiring and
news activity happen constantly.

Fuller Focus described their stack as calling APIs from an LLM. LangGraph was considered
and dropped for this V1: a short sequential pipeline did not need orchestration overhead,
and the intelligence lives in the prompts. The same steps could be wrapped in LangGraph
later if the team wants branching or human-in-the-loop reviews.

---

SETUP

cp .env.example .env
pip install -r requirements.txt

Add your keys to .env:
GEMINI_API_KEY (or GOOGLE_API_KEY; optional GEMINI_MODEL, default gemini-2.5-flash)
TAVILY_API_KEY
HUNTER_API_KEY (optional, contact enrichment)
SENDGRID_API_KEY and FROM_EMAIL (optional, for --send-emails)

Run:
python main.py --query "Find nonprofits recently hiring fundraising leadership"

Output: output/report_TIMESTAMP.html and output/results_TIMESTAMP.json

---

OUTPUT JSON: WHAT EACH FIELD MEANS (AND HOW IT IS PRODUCED)

Each object in `results` is one nonprofit the pipeline considered. Nothing here is random
or hardcoded: org facts come from APIs; scores and prose are produced by Gemini from
that bundle in a single scoring pass (see `utils/scorer.py`).

| Field | Source | What it represents |
| ----- | ------ | ------------------- |
| **name** | ProPublica search + org detail | Legal org name from the 990 explorer API. |
| **score** | Gemini (0–100) | Model judgment of how likely the org is to need an external agency *now*, using only the inputs below. Prompt asks for conservative scores when data is thin. Not a statistical conversion model. |
| **data_quality** | Gemini | `"strong"` if hiring + news + financial all have usable content, `"moderate"` if two do, `"weak"` if one or none (per scorer rules). |
| **mixed_signal** | Gemini | `true` when signals point different ways (e.g. revenue down but senior hiring up). `false` when not contradictory or when there is almost no signal. |
| **financial_signal** | Gemini (summarises ProPublica) | Short prose about revenue / trend passed in from 990 filings. Can read `"unknown"` or similar when ProPublica returned no revenue or trend. |
| **hiring_signal** | Gemini (interprets Tavily) | Summary of web snippets from Tavily for `{org name} + hiring + signal hint`. If search hits generic articles not about that org, the model is instructed to say so (as in your *Nonprofit It* example). |
| **news_signal** | Gemini (interprets Tavily) | Same idea for news / campaigns / grants snippets. Generic industry content gets flagged as not org-specific. |
| **reasoning** | Gemini | Plain-language explanation tying score to the three signal lines. Good for sales QA and for spotting weak leads. |
| **outreach_subject** | Gemini | Draft email subject. Should align with confirmed signals; for weak leads it may be generic on purpose. |
| **outreach_email** | Gemini | Draft body (prompt caps length). Must not claim facts that are not in the signals; weak-signal orgs often get cautious copy. |
| **contact** | Hunter.io (top 5 only) | Added after scoring: email/name/title from domain search. Omitted or empty on lower-ranked rows. |

**Example: low score + weak data_quality**

When ProPublica returns a small org and Tavily returns only generic pages (not about that
nonprofit), Gemini should score low and mark **data_quality** `"weak"`. That is the
system working as designed: honest uncertainty instead of fake precision.

---

METHODOLOGY

Step 1: Query intent extraction
Gemini reads the query and extracts sector, signal type, and geography. This means the
agent understands the query before acting on it. A query for education nonprofits
produces different search parameters than one for hunger relief. No hardcoding.

Step 2: Financial signals via ProPublica
Free 990 API. 1.8M US nonprofits. Pulls revenue for last 3 years and calculates trend.
Growing revenue means budget exists. Declining revenue is flagged as a risk.

Step 3: Hiring signals via Tavily
Searches job boards and career pages for recent senior hires in fundraising, development,
and marketing. A nonprofit hiring a Director of Development is about to spend money on
those services. This is the strongest buying signal in the dataset.

Step 4: News and activity signals via Tavily
Searches for recent campaign launches, grant announcements, new initiatives. Confirms
the org is in an active spending phase, not a quiet maintenance phase.

Step 5: Scoring via Gemini
All three signal sets per org are sent to Gemini in one call. Gemini returns a score 0
to 100 with written reasoning explaining exactly why each org scored high. If signals
contradict each other, for example revenue declining but senior hiring active, Gemini
flags this as a mixed signal and explains both interpretations. Data quality is rated
strong, moderate, or weak based on how many signals had real content.

Step 6: Contact enrichment via Hunter.io
For the top 5 orgs, Tavily finds the real website URL first, extracts the domain, then
Hunter.io searches for decision maker emails on that domain. Confidence is rated
verified or likely based on Hunter's own confidence score.

Step 7: HTML report and JSON output
A dark minimal HTML report with scored cards, signal details, copy-to-clipboard outreach
emails, and CSV export. The JSON output maps directly to HubSpot, Airtable, or any CRM.

---

TOOLS AND TECH

ProPublica Nonprofit Explorer API: free, no key, real 990 data, 1.8M US orgs
Tavily: built for AI agents, handles job board and news searches, free tier 1000/month
Google Gemini (default gemini-2.5-flash): query parsing, signal scoring, email generation
Hunter.io: contact enrichment, free tier 25 lookups/month
Python, requests, python-dotenv

---

COST / SCALE / FEASIBILITY

Per run: ProPublica free, Tavily $0.01, Gemini (varies by model/tier), Hunter free tier
Total: approximately $0.15 per full report

At 100 reports per day: under $600 per month
Profitable inside any subscription above $99 per month

Bottlenecks at scale:
- Hunter.io free tier exhausts quickly, upgrade to paid ($49/month) or switch to Apollo.io
- Tavily free tier is 1000 searches/month, paid tier removes this
- ProPublica has no published rate limit but requests include a 0.3s delay

US nonprofits only. ProPublica covers the US. International support requires Candid API.

---

LIMITATIONS

990 data is 12 to 18 months delayed by IRS filing timelines. Financial signals are
reliable history, not real-time state.

LinkedIn scraping is blocked industry-wide. Job boards and company career pages are the
proxy. Signal quality for smaller orgs with no web presence is lower.

Email enrichment is best-attempt. Confidence levels reflect this honestly. Email
verification is not done in v1.

LLM scoring is reasoning-based, not trained on conversion data. Scores reflect signal
strength, not calibrated probability of closing. With Fuller Focus historical customer
data this becomes a trained classifier.

US only. ProPublica does not cover international nonprofits.

Google Gemini free tier enforces low per-minute and per-day request limits. Heavy testing
or back-to-back runs can return HTTP 429 until the window resets; the code retries with
backoff, but a daily cap still requires waiting until the next day or upgrading the API plan.

---

PLUGGING INTO A WORKFLOW

The JSON output structure maps directly to CRM fields. To push results into HubSpot,
Airtable, or Google Sheets automatically, add a Zapier webhook that watches the output
folder and posts new JSON files on creation. The CSV export in the HTML report handles
manual import to any spreadsheet tool.

---

WHAT I WOULD BUILD NEXT

Scheduled weekly run with diff against previous results, only surfacing new signals
Email verification via NeverBounce before outreach emails go out
Trained scoring model using Fuller Focus actual customer conversion data
International nonprofit support via Candid API
Apollo.io as Hunter fallback for better contact coverage
Simple web UI so non-technical team members can run queries without terminal

---

BONUS: SENDING OUTREACH EMAILS

The agent can send the generated outreach emails directly via SendGrid.

Add to .env:
SENDGRID_API_KEY=your_key_here
FROM_EMAIL=you@yourdomain.com
FROM_NAME=Your Name

Run with the flag:
python main.py --query "Find nonprofits recently hiring fundraising leadership" --send-emails

What happens:
- Agent runs the full pipeline as normal
- For each of the top 5 orgs where a contact email was found, it sends the
  pre-written personalised outreach email via SendGrid
- Each email references the specific signal that made that org score high
- Send status is logged to terminal and saved in the JSON output
- If no SENDGRID_API_KEY is set, it skips silently and still generates the report

SendGrid free tier: 100 emails per day, no credit card required.
Sign up at sendgrid.com, verify a sender email, get an API key.

This is off by default. Default run always generates the report only.
Email sending is an explicit opt-in action.

---

SUBMISSION CHECKLIST (FULLER FOCUS TAKE-HOME)

Aligned with the assessment brief:

| Requirement | Where |
| ----------- | ----- |
| 1. Problem statement | PROBLEM STATEMENT |
| 2. Value | VALUE |
| 3. Why this approach | WHY THIS APPROACH |
| 4. MVP (V1 shipped) | METHODOLOGY + SETUP + repo code |
| 5. Methodology | METHODOLOGY |
| 6. Tools & tech | TOOLS AND TECH |
| 7. Cost / scale / feasibility | COST / SCALE / FEASIBILITY |
| 8. Limitations | LIMITATIONS |
| Trade-offs & “what next” | WHAT I WOULD BUILD NEXT; NOTES.md |
| Example output | `example_output/example.json`, `example_report.html`, and `example_query_education_texas.json` (education + Texas + hiring query). Fresh runs write to `output/` (gitignored). |

**Messiness handling:** Retries on Tavily (in `utils/search.py`), ProPublica search fallbacks and 404 handling (`utils/propublica.py`, `main.py`), Gemini rate-limit retries (`utils/gemini_llm.py`), conservative LLM scoring when signals are weak.

**Optional bonus:** SendGrid outreach via `--send-emails` (see BONUS section).

Clone the repo, copy `.env.example` to `.env`, add keys, then run `python main.py --query "..."`.
