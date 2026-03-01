import os
import json
from dotenv import load_dotenv
from pathlib import Path
from groq import Groq

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Specify the path to the audio file
filename = (
    os.path.dirname(__file__) + "/CalleMiami.m4a"
)  # Replace with your audio file!

# Open the audio file
with open(filename, "rb") as file:
    # Create a transcription of the audio file
    transcription = client.audio.transcriptions.create(
        file=file,  # Required audio file
        model="whisper-large-v3-turbo",  # Required model to use for transcription
        prompt="Specify context or spelling",  # Optional
        response_format="verbose_json",  # Optional
        timestamp_granularities=[
            "word",
            "segment",
        ],  # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
        language="en",  # Optional
        temperature=0.0,  # Optional
    )
    # To print only the transcription text, you'd use print(transcription.text) (here we're printing the entire transcription object to access timestamps)
    print(json.dumps(transcription, indent=2, default=str))
