import sys
import json
from transcript_agent import transcript_agent
from risk_agent import risk_agent
from explainer_agent import explainer_agent, text_to_speech

def run_pipeline(audio_file_path: str, target_language: str = "hi"):
    print(f"--- [1/3] Transcribing Audio: {audio_file_path} ---")
    stt_result = transcript_agent(audio_file_path)
    print(f"Transcript: {stt_result['transcript']}\n")

    print("--- [2/3] Evaluating Scam Risk ---")
    risk_result = risk_agent(stt_result['transcript'])
    print(f"Risk Assessment: {json.dumps(risk_result, indent=2)}\n")

    print(f"--- [3/3] Generating Regional Explanation ({target_language}) ---")
    explanation = explainer_agent(risk_result, language=target_language)
    print(f"Explanation: {explanation['explanation_text']}\n")

    audio_output = text_to_speech(explanation['explanation_text'], language_code="hi-IN")
    print(f"Audio explanation generated at: {audio_output}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        print("Usage: python3 main.py <path_to_audio_file.wav/mp3>")
