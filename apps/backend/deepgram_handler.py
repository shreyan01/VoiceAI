import os
import requests
import json
from pydub import AudioSegment
from io import BytesIO

# Set your Deepgram API key here
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def transcriber(mp3_data):
    try:
        # Prepare the headers with the API key
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav",
        }

        # Prepare the request payload
        payload = mp3_data

        # Prepare the transcription options
        params = {
            "diarize": "true",
            "model": "nova-2"
        }

        # Make the API request
        response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, params=params, data=payload)

        # Parse the response as JSON
        response_json = response.json()

        return response_json

    except Exception as e:
        print(f"Exception: {e}")
        return None