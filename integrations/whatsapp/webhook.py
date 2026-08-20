import os
import httpx
from fastapi import FastAPI, Form, Response
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = FastAPI(title="SuRaksha AI - WhatsApp Integration Service")

twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"), 
    os.getenv("TWILIO_AUTH_TOKEN")
)

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
BACKEND_PIPELINE_URL = os.getenv("MEMBER_A_BACKEND_URL", "http://localhost:8000/webhook")


@app.post("/whatsapp-inbound")
async def whatsapp_inbound(
    From: str = Form(...),
    MediaUrl0: str = Form(None),
    Body: str = Form(None)
):
    """
    Step 3 Intake: Receives inbound webhook from Twilio when a user forwards
    an audio note, extracts the media URL and sender number, then forwards
    the payload to Member A's backend pipeline.
    """
    print(f"\n[INBOUND] Received message from: {From}")
    print(f"[INBOUND] Audio URL: {MediaUrl0}")
    print(f"[INBOUND] Text Body: {Body}")

    payload = {
        "audio_url": MediaUrl0 or "",
        "sender_number": From
    }

    # Forward to Member A's pipeline endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(BACKEND_PIPELINE_URL, json=payload, timeout=10.0)
            print(f"[FORWARD] Pipeline trigger status: {response.status_code}")
        except Exception as exc:
            print(f"[FORWARD ERROR] Could not reach Member A backend: {exc}")

    # Return empty TwiML response to acknowledge receipt
    return Response(content="<Response></Response>", media_type="application/xml")


def send_whatsapp_reply(recipient_number: str, text_message: str, audio_url: str = None):
    """
    Step 4 Reply: Sends the risk badge/summary and voice note back
    to the original user via Twilio WhatsApp.
    """
    message_args = {
        "from_": TWILIO_WHATSAPP_NUMBER,
        "to": recipient_number,
        "body": text_message
    }
    
    if audio_url:
        message_args["media_url"] = [audio_url]

    msg = twilio_client.messages.create(**message_args)
    print(f"[REPLY SENT] SID: {msg.sid} to {recipient_number}")
    return msg.sid