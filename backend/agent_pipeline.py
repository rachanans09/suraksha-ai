import os
import json
import whisper
import anthropic
from dotenv import load_dotenv
from google.cloud import texttospeech

load_dotenv()

# Map language codes to Google Cloud TTS voice configs
TTS_VOICE_MAPPING = {
    "hi": {"language_code": "hi-IN", "name": "hi-IN-Neural2-A"},
    "en": {"language_code": "en-IN", "name": "en-IN-Neural2-A"},
    "ta": {"language_code": "ta-IN", "name": "ta-IN-Neural2-A"},
    "te": {"language_code": "te-IN", "name": "te-IN-Standard-A"},
    "kn": {"language_code": "kn-IN", "name": "kn-IN-Standard-A"},
    "mr": {"language_code": "mr-IN", "name": "mr-IN-Neural2-A"},
    "bn": {"language_code": "bn-IN", "name": "bn-IN-Neural2-A"}
}

def run_transcription(audio_file_path: str) -> dict:
    """Stage 1: Speech-to-Text using OpenAI Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path, fp16=False)
    return {
        "transcript": result.get("text", "").strip(),
        "language": result.get("language", "en"),
        "audio_path": audio_file_path
    }

def run_risk_analysis(transcript: str) -> dict:
    """Stage 2: Scam evaluation via Claude 3.5 Sonnet with local rule fallback."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            patterns_file = os.path.join(os.path.dirname(__file__), "scam_patterns", "patterns.json")
            
            patterns_data = []
            if os.path.exists(patterns_file):
                with open(patterns_file, "r") as f:
                    patterns_data = json.load(f)

            prompt = (
                f"Analyze this call transcript for potential scam/fraud indicators based on these patterns: {json.dumps(patterns_data)}.\n"
                f"Transcript: \"{transcript}\"\n\n"
                f"Return ONLY a valid JSON object with exact keys:\n"
                f"- 'risk_score': integer (0 to 100)\n"
                f"- 'risk_level': string ('LOW', 'MEDIUM', 'HIGH')\n"
                f"- 'detected_patterns': list of string pattern names\n"
                f"- 'reason': string explaining the decision"
            )

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.content[0].text)
        except Exception as e:
            print(f"[Pipeline Notice] Anthropic API failed ({e}). Using local rule engine.")

    # Rule-Based Local Fallback
    t_lower = transcript.lower()
    keywords = ["otp", "blocked", "bank", "immediately", "urgent", "account", "police", "verify"]
    matched = [kw.upper() for kw in keywords if kw in t_lower]
    is_scam = len(matched) >= 2 or "otp" in t_lower

    return {
        "risk_score": 95 if is_scam else 15,
        "risk_level": "HIGH" if is_scam else "LOW",
        "detected_patterns": ["Urgency Pressure", "Sensitive Credential Request", "Banking Impersonation"] if is_scam else [],
        "reason": "High-risk request detected for sensitive account information under urgent threat." if is_scam else "No severe scam indicators detected."
    }

def run_explainer_agent(risk_analysis: dict, language: str = "hi") -> dict:
    """Stage 3: Generate regional guidance text via Claude 3.5 Sonnet."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key:
        try:
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                f"You are a helpful security agent. Explain this risk assessment clearly in simple terms for a non-technical user in language code '{language}': {json.dumps(risk_analysis)}.\n"
                f"Keep it under 3 sentences. Emphasize actionable safety advice.\n"
                f"Return ONLY valid JSON with key 'explanation_text'."
            )
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(response.content[0].text)
        except Exception as e:
            print(f"[Pipeline Notice] Explainer LLM failed ({e}). Using local text template.")

    # Regional Local Text Fallback Templates
    templates = {
        "hi": f"सावधान! यह एक संभावित धोखाधड़ी कॉल है। जोखिम स्तर: {risk_analysis.get('risk_level')}. किसी भी व्यक्ति के साथ अपना बैंक OTP या PIN साझा न करें।",
        "en": f"Warning! This call shows signs of fraud. Risk Level: {risk_analysis.get('risk_level')}. Never share your bank OTP or PIN with anyone.",
        "ta": f"எச்சரிக்கை! இது ஒரு போலி அழைப்பாக இருக்கலாம். அபாய நிலை: {risk_analysis.get('risk_level')}. உங்கள் OTP ஐ யாருடனும் பகிர வேண்டாம்.",
        "te": f"హెచ్చరిక! ఇది మోసపూరిత కాల్ కావచ్చు. ప్రమాద స్థాయి: {risk_analysis.get('risk_level')}. మీ OTP ని ఎవరితోనూ పంచుకోవద్దు."
    }
    return {"explanation_text": templates.get(language, templates["en"])}

def generate_tts_audio(text: str, target_language: str = "hi", output_dir: str = "output_audio") -> str:
    """Stage 4: Convert regional explanation text to an MP3 audio file via Google Cloud TTS."""
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"alert_{os.urandom(4).hex()}.mp3")
    
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice_config = TTS_VOICE_MAPPING.get(target_language, TTS_VOICE_MAPPING["hi"])
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"],
            name=voice_config["name"]
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95
        )

        response = client.synthesize_speech(
            input=synthesis_input, 
            voice=voice, 
            audio_config=audio_config
        )

        with open(output_filename, "wb") as out:
            out.write(response.audio_content)

        return output_filename

    except Exception as e:
        print(f"[Pipeline Notice] Google Cloud TTS skipped ({e}). Passing raw text.")
        return None

def process_audio_call(audio_file_path: str, target_language: str = "hi") -> dict:
    """Main Pipeline Orchestrator Function to be imported into API endpoints."""
    stt = run_transcription(audio_file_path)
    risk = run_risk_analysis(stt["transcript"])
    explanation = run_explainer_agent(risk, language=target_language)
    audio_path = generate_tts_audio(explanation["explanation_text"], target_language=target_language)

    return {
        "status": "success",
        "transcript": stt["transcript"],
        "detected_language": stt["language"],
        "analysis": {
            "risk_score": risk["risk_score"],
            "risk_level": "HIGH" if risk["risk_score"] >= 75 else "MEDIUM" if risk["risk_score"] >= 40 else "LOW",
            "detected_patterns": risk["detected_patterns"],
            "reason": risk["reason"]
        },
        "user_guidance": {
            "text": explanation["explanation_text"],
            "audio_file_path": audio_path,
            "has_audio": audio_path is not None
        }
    }