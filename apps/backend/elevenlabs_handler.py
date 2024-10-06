import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
XI_API_KEY = os.getenv("XI_API_KEY")
print(f"API Key: {XI_API_KEY}") 

headers={
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY
}

def add_voice(name, file_path):
    url = "https://api.elevenlabs.io/v1/voices/add"
    
    with open(file_path, 'rb') as file:
        files = [('files', (file.name, file, 'audio/mpeg'))]
        data = {'name': name}
        
        response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 200:
        return response.json()['voice_id']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Usage
voice_id = add_voice("Speaker_0", "speaker_0.mp3")
# Function to create a custom voice and get the voice_id
def text_to_speech(voice_id, text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        print("Audio generated successfully.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Usage
custom_text = "Hey Shravan! I would really appreciate it if you could give Shreyan this internship opportunity. I think he would be a great fit for the role. Thank you!"
text_to_speech(voice_id, custom_text)