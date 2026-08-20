import os
import json
import anthropic
from google.cloud import texttospeech

def explainer_agent(risk_analysis: dict, language: str = "hi") -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"Explain this risk analysis simply in language code '{language}': {json.dumps(risk_analysis)}. Return JSON with key 'explanation_text'."
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(response.content[0].text)
    except Exception as e:
        print(f"[Fallback Mode Activated] API unavailable ({e}). Generating regional explanation locally...")
        return {
            "explanation_text": f"सावधान! यह एक धोखाधड़ी (Scam) कॉल हो सकती है। जोखिम स्तर: {risk_analysis.get('risk_level')}. कारण: कभी भी किसी के साथ अपना बैंक OTP साझा न करें।"
        }

def text_to_speech(text: str, language_code: str = "hi-IN") -> str:
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        
        output_file = "samples/explanation_output.mp3"
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        return output_file
    except Exception as e:
        print(f"[Notice] Google TTS skipped ({e}). Passing raw text output.")
        return "Audio generation bypassed."
