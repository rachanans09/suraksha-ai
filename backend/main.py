import json
import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import Member B's real pipeline logic and teammate's WhatsApp dispatcher
from agent_pipeline import process_audio_call
from twilio_whatsapp_dispatcher import dispatch_alerts

# Simple .env file reader (zero dependencies)
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def insert_into_supabase(data: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("--- [DB] Supabase credentials not found in environment. Skipping DB insert.")
        return

    url = f"{SUPABASE_URL}/rest/v1/calls"
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "return=minimal"
    }
    
    req_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"--- [DB] Call successfully logged to Supabase! Status: {response.status}")
    except Exception as e:
        print(f"--- [DB ERROR] Failed to insert into Supabase: {e}")

class SimpleWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/docs":
            response = {"status": "healthy", "service": "SuRaksha AI Backend (Native + Supabase + Real AI + WhatsApp Alerts)"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/webhook":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                
                data = json.loads(body.decode("utf-8"))
                audio_url = data.get("audio_url", "https://example.com/default.mp3")
                target_language = data.get("language", "hi")
                user_phone = data.get("phone_number") or os.environ.get("MY_PHONE_NUMBER")
                family_contact = data.get("family_contact")
                
                print(f"--- [PIPELINE] Running real transcription & risk engine for: {audio_url}")
                
                # 1. Run Member B's actual AI processing engine (STT, Claude Risk, TTS)
                result = process_audio_call(audio_url, target_language=target_language)
                
                analysis_info = result.get("analysis", {})
                risk_level_str = analysis_info.get("risk_level", "LOW").lower()
                confidence_val = analysis_info.get("risk_score", 0) / 100.0
                
                risk_payload = {
                    "risk": risk_level_str,
                    "confidence": confidence_val,
                    "reason": analysis_info.get("reason", "Analysis completed.")
                }
                
                # 2. Save structured output to Supabase table ("calls")
                db_payload = {
                    "audio_url": audio_url,
                    "transcript": result.get("transcript", ""),
                    "language": result.get("detected_language", "en"),
                    "risk_score": analysis_info.get("risk_score", 0)
                }
                insert_into_supabase(db_payload)
                
                # 3. Trigger Teammate's WhatsApp Dispatcher if phone number is available
                if user_phone:
                    print(f"--- [WHATSAPP] Dispatching alerts to user: {user_phone}")
                    dispatch_alerts(
                        sender_number=user_phone,
                        risk_data=risk_payload,
                        transcript_text=result.get("transcript", ""),
                        explanation_text=result.get("user_guidance", {}).get("text"),
                        family_contact=family_contact
                    )
                else:
                    print("--- [WHATSAPP NOTICE] No recipient phone number provided in webhook payload or environment.")
                
                response_bytes = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
                
            except Exception as e:
                err_bytes = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_bytes)))
                self.end_headers()
                self.wfile.write(err_bytes)
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleWebhookHandler)
    print(f"SuRaksha AI Native Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()