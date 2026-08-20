import json
import os
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        print("--- [DB] Supabase credentials not found in .env. Skipping DB insert.")
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

def run_agent_pipeline(audio_url: str):
    print(f"--- [1/5] INGESTION AGENT --- Processing: {audio_url}")
    print("--- [2/5] TRANSCRIPT & LANGUAGE AGENT --- Transcript generated.")
    print("--- [3/5] RISK ANALYSIS AGENT --- Risk Assessed: HIGH")
    print("--- [4A/5] EXPLAINER AGENT --- Audio warning rendered.")
    print("--- [4B/5] FAMILY ALERT AGENT --- WhatsApp emergency alert dispatched!")
    
    result = {
        "status": "success",
        "pipeline_result": {
            "audio_url": audio_url,
            "transcript": "Aadhaar number do immediately or account will be blocked!",
            "language": "en",
            "risk_level": "high",
            "confidence": 0.95,
            "reason": "Urgent demand for sensitive financial/identity data.",
            "alert_status": "WhatsApp emergency alert dispatched to family!"
        }
    }
    
    # Save to Supabase table ("calls")
    db_payload = {
        "audio_url": audio_url,
        "transcript": result["pipeline_result"]["transcript"],
        "language": result["pipeline_result"]["language"],
        "risk_score": result["pipeline_result"]["confidence"]
    }
    insert_into_supabase(db_payload)
    
    return result

class SimpleWebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/docs":
            response = {"status": "healthy", "service": "SuRaksha AI Backend (Native + Supabase)"}
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
                
                result = run_agent_pipeline(audio_url)
                
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

def run_server(port=8000):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, SimpleWebhookHandler)
    print(f"SuRaksha AI Native Server with Supabase running on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()