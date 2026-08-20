import urllib.request
import json

url = "http://127.0.0.1:8000/webhook"
payload = json.dumps({"audio_url": "https://example.com/scam-call.mp3"}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        print("Response from server:")
        print(response.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)