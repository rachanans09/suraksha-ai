import os
import json
import anthropic
from google.cloud import texttospeech
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def explainer_agent(risk_data: dict, language: str = "hi") -> dict:
    prompt = f"""
    Risk evaluation: {json.dumps(risk_data)}
    Target Language Code: {language}

    Translate and simplify this risk explanation into 1-2 spoken-language sentences for a low-literacy user.
    For example in Hindi: "Yeh call ek dhokha ho sakta hai — bank kabhi OTP nahi maangta."
    Respond ONLY with the text explanation.
    """

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    
    explanation_text = response.content[0].text.strip()
    return {"explanation_text": explanation_text, "language": language}

def text_to_speech(text: str, language_code: str = "hi-IN", output_path: str = "output.mp3"):
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    
    return output_path
