import argparse
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from utils.propublica import get_nonprofits
from utils.search import hiring_signals, news_signals
from utils.scorer import score_orgs
from utils.enricher import enrich_contact
from utils.report_generator import generate_report
from utils.query_parser import parse_query
from utils.mailer import send_outreach_emails

def run(query, send_emails=False):
    print(f"Query received: {query}")

    intent = parse_query(query)
    if not intent:
        print("Could not parse query intent. Try something more specific.")
        print("Example: Find nonprofits recently hiring fundraising leadership")
        return

    print(f"Understood: sector={intent.get('sector')} signal={intent.get('signal')} location={intent.get('location') or 'any'}")

    search_q = intent.get("sector") or intent.get("signal") or query
    if len(search_q) > 120:
        search_q = intent.get("signal") or intent.get("sector") or "nonprofit"
    orgs = get_nonprofits(search_q)
    if not orgs and search_q.lower() not in ("nonprofit", "charity", "charitable"):
        print(f'No ProPublica matches for "{search_q}". Trying broader search "nonprofit"...')
        orgs = get_nonprofits("nonprofit")
    if not orgs:
        print("No orgs found. ProPublica returned nothing for this query.")
        return

    print(f"Found {len(orgs)} orgs from ProPublica. Fetching signals...")

    for org in orgs:
        org["hiring"] = hiring_signals(org["name"], intent.get("signal", ""))
        org["news"] = news_signals(org["name"])
        time.sleep(0.3)

    ranked = score_orgs(query, intent, orgs)
    if not ranked:
        print("Scoring failed. Check your GEMINI_API_KEY (or GOOGLE_API_KEY).")
        return

    print(f"Scored {len(ranked)} orgs. Enriching top 5 contacts...")

    for org in ranked[:5]:
        org["contact"] = enrich_contact(org["name"])

    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if send_emails:
        from_email = os.getenv("FROM_EMAIL")
        from_name = os.getenv("FROM_NAME", "Fuller Focus")
        orgs_with_contact = [o for o in ranked[:5] if o.get("contact", {}).get("email")]

        if not orgs_with_contact:
            print("No contacts found to email.")
        else:
            print(f"\nSending outreach emails to {len(orgs_with_contact)} contacts...")
            email_log = send_outreach_emails(orgs_with_contact, from_email, from_name)
            for org, result in zip(orgs_with_contact, email_log):
                org["email_sent"] = result.get("status") == "sent"

    json_path = f"output/results_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump({"query": query, "intent": intent, "timestamp": timestamp, "results": ranked}, f, indent=2)

    html_path = f"output/report_{timestamp}.html"
    generate_report(query, ranked, html_path)

    print(f"\nDone. {len(ranked)} orgs ranked.")
    print(f"Report: {html_path}")
    print(f"JSON:   {json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Natural language query")
    parser.add_argument("--send-emails", action="store_true", help="Send outreach emails via SendGrid (requires SENDGRID_API_KEY and FROM_EMAIL in .env)")
    args = parser.parse_args()
    run(args.query, send_emails=args.send_emails)
