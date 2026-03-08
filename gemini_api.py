import os
import time
from google import genai
from dotenv import load_dotenv

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
load_dotenv()
def get_gemini():
    gemini_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    session = client.files.upload(file="session.mp4")
    
    while session.state.name != "ACTIVE":
        time.sleep(2)
        session = client.files.get(name=session.name)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[session, "Analyze my performance doing a badminton drill of clears."]
    )
    return response.text

