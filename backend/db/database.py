import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_supabase_connection():
    """Test script to insert and read back a row from the calls table."""
    try:
        # Insert test row
        test_data = {
            "audio_url": "https://example.com/test-audio.mp3",
            "transcript": "This is a test transcript.",
            "language": "en",
            "risk_score": 0.1
        }
        insert_res = supabase.table("calls").insert(test_data).execute()
        print(" Supabase Insert Success:", insert_res.data)
        
        # Read back the row
        row_id = insert_res.data[0]["id"]
        read_res = supabase.table("calls").select("*").eq("id", row_id).execute()
        print(" Supabase Read Success:", read_res.data)
        
        return True
    except Exception as e:
        print(" Supabase Connection Failed:", str(e))
        return False

if __name__ == "__main__":
    test_supabase_connection()