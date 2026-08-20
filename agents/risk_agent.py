import os
import json
import anthropic

def risk_agent(transcript: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        with open("scam_patterns/patterns.json", "r") as f:
            patterns = json.load(f)

        prompt = f"Analyze this transcript for scam indicators using these patterns: {json.dumps(patterns)}.\nTranscript: {transcript}\nReturn pure JSON with keys: risk_score (0-100), risk_level (LOW/MEDIUM/HIGH), detected_patterns (list), reason."

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"[Fallback Mode Activated] API unavailable ({e}). Running local rule-based engine...")
        t_lower = transcript.lower()
        is_scam = any(kw in t_lower for kw in ["otp", "blocked", "bank", "immediately", "urgent"])
        return {
            "risk_score": 95 if is_scam else 10,
            "risk_level": "HIGH" if is_scam else "LOW",
            "detected_patterns": ["Urgency Pressure", "OTP Request", "Banking Impersonation"] if is_scam else [],
            "reason": "Detected urgent demand for sensitive banking credentials (OTP/Account lock threat)." if is_scam else "No common scam keywords found."
        }
