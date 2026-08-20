import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from twilio.rest import Client

# Automatically search for .env in current and parent directories
load_dotenv(find_dotenv())

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
to_whatsapp = os.getenv("MY_PHONE_NUMBER")

# Sanity check to verify variables loaded
if not account_sid or not auth_token:
    raise ValueError(
        "Credentials missing! Ensure a valid .env file exists in the project root with TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN."
    )

print(f"Loaded SID: {account_sid[:6]}... (valid format)")

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hello from SuRaksha AI! Your standalone WhatsApp integration is working.",
    from_=from_whatsapp,
    to=to_whatsapp
)

print(f"Message sent successfully! Message SID: {message.sid}")