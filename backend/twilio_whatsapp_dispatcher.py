import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
DEFAULT_FAMILY_CONTACT = os.getenv("MY_PHONE_NUMBER")

# Initialize Twilio Client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def format_whatsapp_number(number: str) -> str:
    """Ensures phone number has the 'whatsapp:' prefix."""
    number = number.strip()
    if not number.startswith("whatsapp:"):
        return f"whatsapp:{number}"
    return number


def send_user_report(
    recipient_number: str,
    risk_data: Dict[str, Any],
    transcript_preview: Optional[str] = None,
    explanation_text: Optional[str] = None
) -> Optional[str]:
    """
    Sends the primary scam analysis report back to the user who submitted the audio.
    """
    risk_level = str(risk_data.get("risk", "low")).strip().lower()
    confidence = float(risk_data.get("confidence", 0.0))
    confidence_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
    reason = risk_data.get("reason", "Analysis completed.")

    if risk_level == "high":
        badge = "🚨 *HIGH RISK SCAM DETECTED*"
        action_advice = "⛔ *DO NOT* share OTPs, click suspicious links, or transfer funds."
    elif risk_level == "medium":
        badge = "⚠️ *SUSPICIOUS CALL DETECTED*"
        action_advice = "🔍 Verify the caller independently before taking any action."
    else:
        badge = "✅ *SAFE CALL / LOW RISK*"
        action_advice = "No immediate scam indicators identified."

    message_lines = [
        "🛡️ *SuRaksha AI — Analysis Report*",
        "------------------------------------",
        f"{badge}",
        f"• *Confidence Score:* {confidence_percent}%",
        f"• *Primary Finding:* {reason}",
    ]

    if explanation_text:
        message_lines.extend(["", f"🗣️ *Explanation:*", f"{explanation_text}"])

    if transcript_preview:
        preview = (transcript_preview[:120] + "...") if len(transcript_preview) > 120 else transcript_preview
        message_lines.extend(["", f"📝 *Transcript Snippet:*", f"_{preview}_"])

    message_lines.extend(["", action_advice])
    body = "\n".join(message_lines)

    try:
        msg = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=format_whatsapp_number(recipient_number),
            body=body
        )
        print(f"[ALERT DISPATCHER] User report sent. SID: {msg.sid}")
        return msg.sid
    except Exception as exc:
        print(f"[ALERT DISPATCHER ERROR] Failed to send user report: {exc}")
        return None


def send_family_alert(
    risk_data: Dict[str, Any],
    target_family_number: Optional[str] = None,
    caller_info: Optional[str] = None
) -> Optional[str]:
    """
    Dispatches a high-priority alert to the registered family member if the call is high risk.
    """
    risk_level = str(risk_data.get("risk", "")).strip().lower()
    if risk_level != "high":
        print(f"[ALERT DISPATCHER] Family alert skipped — risk is '{risk_level}'.")
        return None

    recipient = target_family_number or DEFAULT_FAMILY_CONTACT
    if not recipient:
        print("[ALERT DISPATCHER ERROR] No family contact configured.")
        return None

    confidence = float(risk_data.get("confidence", 0.0))
    confidence_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
    reason = risk_data.get("reason", "Potential fraudulent interaction detected.")
    caller_tag = f"from *{caller_info}*" if caller_info else "received by your family member"

    alert_body = (
        f"🚨 *SuRaksha AI — Urgent Family Scam Alert*\n\n"
        f"A call {caller_tag} was flagged as *HIGH RISK SCAM*.\n\n"
        f"• *Risk Score:* {confidence_percent}%\n"
        f"• *Threat Detected:* {reason}\n\n"
        f"⚠️ *Recommended Action:* Contact them immediately to ensure they do not authorize any transactions or reveal passwords."
    )

    try:
        msg = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=format_whatsapp_number(recipient),
            body=alert_body
        )
        print(f"[ALERT DISPATCHER] Family emergency alert sent to {recipient}. SID: {msg.sid}")
        return msg.sid
    except Exception as exc:
        print(f"[ALERT DISPATCHER ERROR] Failed to send family alert: {exc}")
        return None


def dispatch_alerts(
    sender_number: str,
    risk_data: Dict[str, Any],
    transcript_text: Optional[str] = None,
    explanation_text: Optional[str] = None,
    family_contact: Optional[str] = None
) -> Dict[str, Any]:
    """
    Master dispatch coordinator: Sends the report to the user and triggers
    family escalation if high risk.
    """
    user_sid = send_user_report(
        recipient_number=sender_number,
        risk_data=risk_data,
        transcript_preview=transcript_text,
        explanation_text=explanation_text
    )

    family_sid = None
    if str(risk_data.get("risk", "")).lower() == "high":
        family_sid = send_family_alert(
            risk_data=risk_data,
            target_family_number=family_contact,
            caller_info=sender_number.replace("whatsapp:", "")
        )

    return {
        "user_notification_sid": user_sid,
        "family_alert_sid": family_sid,
        "status": "delivered" if user_sid else "failed"
    }


if __name__ == "__main__":
    test_risk = {
        "risk": "high",
        "confidence": 0.96,
        "reason": "Impersonation of electricity board official demanding immediate payment via unverified link."
    }
    test_transcript = "Your electricity will be cut off tonight at 9:30 PM. Pay via link immediately."
    test_explanation = "यह कॉल बिजली विभाग का होने का ढोंग कर रही है। किसी भी लिंक पर क्लिक न करें।"

    print("Running standalone dispatcher test...")
    if DEFAULT_FAMILY_CONTACT:
        res = dispatch_alerts(
            sender_number=DEFAULT_FAMILY_CONTACT,
            risk_data=test_risk,
            transcript_text=test_transcript,
            explanation_text=test_explanation
        )
        print("Dispatch results:", res)
    else:
        print("Set MY_PHONE_NUMBER in .env to run standalone dispatch test.")