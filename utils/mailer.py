import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_outreach_emails(orgs, from_email, from_name):
    key = os.getenv("SENDGRID_API_KEY")
    if not key:
        print("No SENDGRID_API_KEY set. Skipping send.")
        return []

    if not from_email:
        print("No FROM_EMAIL set. Skipping send.")
        return []

    client = SendGridAPIClient(api_key=key)
    sent = []
    failed = []

    for org in orgs:
        contact = org.get("contact") or {}
        to_email = contact.get("email")

        if not to_email:
            print(f"  Skipped {org.get('name')}: no email found")
            continue

        subject = org.get("outreach_subject", "Introduction")
        body = org.get("outreach_email", "")

        message = Mail(
            from_email=(from_email, from_name),
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )

        try:
            resp = client.send(message)
            if resp.status_code in (200, 202):
                sent.append({"org": org.get("name"), "to": to_email, "status": "sent"})
                print(f"  Sent to {org.get('name')} at {to_email}")
            else:
                failed.append({"org": org.get("name"), "to": to_email, "status": f"failed:{resp.status_code}"})
                print(f"  Failed {org.get('name')}: status {resp.status_code}")
        except Exception as e:
            failed.append({"org": org.get("name"), "to": to_email, "status": f"error:{str(e)}"})
            print(f"  Error sending to {org.get('name')}: {e}")

    print(f"\nEmail summary: {len(sent)} sent, {len(failed)} failed")
    return sent + failed
