import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def risk_agent(transcript: str) -> dict:
    with open("scam_patterns/patterns.json", "r") as f:
        scam_patterns = json.load(f)

    prompt = f"""
    Scam patterns knowledge base:
    {json.dumps(scam_patterns, indent=2)}

    Transcript to evaluate:
    "{transcript}"

    Analyze if this transcript matches any scam pattern.
    Respond strictly with a JSON object containing keys:
    - risk ("low" | "medium" | "high")
    - confidence (float between 0.0 and 1.0)
    - reason (short text string explanation)
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
