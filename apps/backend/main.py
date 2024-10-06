from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from pydub import AudioSegment
import os
import requests
import json
from io import BytesIO
from dotenv import load_dotenv
import logging
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv(dotenv_path=".env")

app = FastAPI()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
XI_API_KEY = os.getenv("XI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://voice-ai-rouge.vercel.app", "https://voice-ai-rouge.vercel.app/generate-audio"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add these environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")

def upload_to_s3(local_file, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
    try:
        s3.upload_file(local_file, S3_BUCKET, s3_file)
        return True
    except FileNotFoundError:
        logger.error("The file was not found")
        return False
    except NoCredentialsError:
        logger.error("Credentials not available")
        return False

@app.post("/process_audio/")
async def process_audio(file: UploadFile = File(...), text: str = Form(...)):
    try:
        logger.info("Received file: %s", file.filename)
        
        # Step 1: Upload and process the audio/video file
        content = await file.read()
        
        if file.filename.lower().endswith('.mp4'):
            audio = AudioSegment.from_file(BytesIO(content), format="mp4")
            output_file = "input_audio.mp3"
            audio.export(output_file, format="mp3")
        elif file.filename.lower().endswith('.mp3'):
            output_file = "input_audio.mp3"
            with open(output_file, "wb") as f:
                f.write(content)
        else:
            return JSONResponse(content={"message": "Unsupported file format. Please upload MP3 or MP4."}, status_code=400)
        
        logger.info("File saved successfully: %s", output_file)
        
        # Upload to S3
        
        # Step 2: Transcribe the audio with diarization
        transcription_result = await transcribe_audio()
        
        # Step 3: Extract speaker segments
        speaker_segments = await extract_speaker_segments()
        
        # Step 4: Generate speech from custom text using the first speaker
        if speaker_segments:
            first_speaker = min(speaker_segments.keys())
            generated_speech = await generate_speech_from_speaker(first_speaker, text)
            return generated_speech
        else:
            return JSONResponse(content={"message": "No speakers detected in the audio."}, status_code=400)
        
    except Exception as e:
        logger.error("Error processing audio: %s", e)
        return JSONResponse(content={"message": f"Error processing audio: {e}"}, status_code=500)

@app.post("/transcribe_audio/")
async def transcribe_audio():
    try:
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/mpeg"
        }
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "diarize": "true"
        }
        
        with open("input_audio.mp3", "rb") as audio_file:
            response = requests.post(url, headers=headers, params=params, data=audio_file)
        
        # Check for errors
        response.raise_for_status()
        
        response_json = response.json()
        with open("output.json", "w") as file:
            json.dump(response_json, file, indent=4)
        
        return response_json  # Return the actual JSON data
    except requests.exceptions.RequestException as e:
        logger.error("Error connecting to Deepgram API: %s", e)
        return JSONResponse(content={"message": f"Error connecting to Deepgram API: {e}"}, status_code=500)
    except Exception as e:
        logger.error("Error transcribing audio: %s", e)
        return JSONResponse(content={"message": f"Error transcribing audio: {e}"}, status_code=500)

@app.post("/extract_speaker_segments/")
async def extract_speaker_segments():
    try:
        with open("output.json", 'r') as file:
            data = json.load(file)
        audio = AudioSegment.from_mp3("input_audio.mp3")
        speaker_segments = {}
        for word_data in data['results']['channels'][0]['alternatives'][0]['words']:
            speaker = word_data['speaker']
            start_time = word_data['start'] * 1000
            end_time = word_data['end'] * 1000
            segment = audio[start_time:end_time]
            if speaker in speaker_segments:
                speaker_segments[speaker] += segment
            else:
                speaker_segments[speaker] = segment
        for speaker, segment in speaker_segments.items():
            segment.export(f"speaker_{speaker}.mp3", format="mp3")
        return speaker_segments  # <- Return the actual dictionary here
    except Exception as e:
        logger.error("Error extracting speaker segments: %s", e)
        return JSONResponse(content={"message": f"Error extracting speaker segments: {e}"}, status_code=500)

@app.post("/generate_speech_from_speaker/")
async def generate_speech_from_speaker(speaker_id: int, text: str):
    try:
        # Add the speaker's voice to Eleven Labs
        url = "https://api.elevenlabs.io/v1/voices/add"
        headers = {
            "Accept": "application/json",
            "xi-api-key": XI_API_KEY
        }
        file_path = f"speaker_{speaker_id}.mp3"
        with open(file_path, 'rb') as f:
            files = [('files', (f.name, f, 'audio/mpeg'))]
            data = {'name': f"Speaker_{speaker_id}"}
            response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code == 200:
            voice_id = response.json()['voice_id']
        else:
            return JSONResponse(content={"message": f"Error: {response.status_code}, {response.text}"}, status_code=response.status_code)
        
        # Generate speech from custom text using the speaker's voice
        return await text_to_speech(voice_id, text)
    except Exception as e:
        logger.error("Error generating speech from speaker: %s", e)
        return JSONResponse(content={"message": f"Error generating speech from speaker: {e}"}, status_code=500)

@app.post("/text_to_speech/")
async def text_to_speech(voice_id: str, text: str):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "application/json",
            "xi-api-key": XI_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.9
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open("output.mp3", "wb") as f:
                f.write(response.content)
            return FileResponse("output.mp3", media_type="audio/mpeg", filename="output.mp3")
        else:
            return JSONResponse(content={"message": f"Error: {response.status_code}, {response.text}"}, status_code=response.status_code)
    except Exception as e:
        logger.error("Error generating speech: %s", e)
        return JSONResponse(content={"message": f"Error generating speech: {e}"}, status_code=500)