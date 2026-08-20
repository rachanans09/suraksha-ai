import os
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"), 
    os.getenv("TWILIO_AUTH_TOKEN")
)

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
DEFAULT_FAMILY_CONTACT = os.getenv("MY_PHONE_NUMBER")


def trigger_family_alert(risk_data: dict, family_contact: str = None) -> bool:
    """
    Step 5 Family Alert: Fires a high-priority WhatsApp notification to a
    pre-registered family contact when the risk verdict is 'high'.
    """
    risk_level = str(risk_data.get("risk", "")).strip().lower()
    confidence = risk_data.get("confidence", 0.0)
    reason = risk_data.get("reason", "Potential fraudulent interaction detected.")

    # Only fire alerts for high-risk verdicts
    if risk_level != "high":
        print(f"[FAMILY ALERT] Skipped — risk level is '{risk_level}'")
        return False

    target_number = family_contact or DEFAULT_FAMILY_CONTACT
    if not target_number:
        print("[FAMILY ALERT ERROR] No family contact number configured.")
        return False

    confidence_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
    
    alert_body = (
        f"🚨 *SuRaksha AI — High Risk Scam Alert*\n\n"
        f"An audio call analyzed for your family member was flagged as *HIGH RISK*.\n"
        f"• *Risk Score:* {confidence_percent}%\n"
        f"• *Reason:* {reason}\n\n"
        f"Please check in with them immediately to prevent unauthorized transfers."
    )

    try:
        msg = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=target_number,
            body=alert_body
        )
        print(f"[FAMILY ALERT SENT] SID: {msg.sid} to {target_number}")
        return True
    except Exception as exc:
        print(f"[FAMILY ALERT ERROR] Failed to send alert: {exc}")
        return False


if __name__ == "__main__":
    # Standalone verification test with mock high-risk verdict
    print("Testing trigger_family_alert standalone...")
    mock_payload = {
        "risk": "high",
        "confidence": 0.94,
        "reason": "Caller claimed to be from bank demanding urgent OTP confirmation."
    }
    trigger_family_alert(mock_payload)
    