import whisper

def transcript_agent(audio_path: str) -> dict:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    
    return {
        "transcript": result["text"],
        "language": result["language"],
        "audio_url": audio_path
    }
