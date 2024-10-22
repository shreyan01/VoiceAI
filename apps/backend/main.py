from fastapi import FastAPI, File, UploadFile, Form, HTTPException
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
import yt_dlp

load_dotenv(dotenv_path=".env")

app = FastAPI()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
UPLOAD_URL = os.getenv("UPLOAD_URL")
TRANSCRIBE_URL = os.getenv("TRANSCRIBE_URL")
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
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
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
        input_file = "input_audio.mp3"
        
        if not os.path.exists(input_file):
            raise HTTPException(status_code=404, detail="Input audio file not found")

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Authorization": f"token {DEEPGRAM_API_KEY}",
            "Origin": "https://playground.deepgram.com",
            "Connection": "keep-alive",
        }

        # Step 1: Upload the file
        with open(input_file, "rb") as f:
            files = {"file": f}
            logger.info(f"Uploading file to {UPLOAD_URL}")
            upload_response = requests.post(UPLOAD_URL, headers=headers, files=files)

        if upload_response.status_code not in (200, 201):
            logger.error(f"Error during upload: {upload_response.status_code}")
            raise HTTPException(status_code=500, detail="Failed to upload file to Deepgram")

        asset_id = upload_response.json().get("asset")
        if not asset_id:
            logger.error("Asset ID not found in upload response.")
            raise HTTPException(status_code=500, detail="Asset ID not found in upload response")

        # Step 2: Request transcription
        transcribe_data = {
            "url": f"https://manage.deepgram.com/storage/assets/{asset_id}"
        }
        logger.info(f"Requesting transcription from {TRANSCRIBE_URL}")
        transcribe_response = requests.post(
            TRANSCRIBE_URL,
            headers=headers,
            json=transcribe_data,
        )

        if transcribe_response.status_code not in (200, 201):
            logger.error(f"Error during transcription: {transcribe_response.status_code}")
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")

        # Parse the JSON response
        transcript_data = transcribe_response.json()

        # Save the transcript to a file
        with open("output.json", "w") as file:
            json.dump(transcript_data, file, indent=4)
        
        logger.info("Transcription completed and saved to output.json")
        return transcript_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Deepgram API: {e}")
        raise HTTPException(status_code=500, detail=f"Error connecting to Deepgram API: {str(e)}")
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")

@app.post("/extract_speaker_segments/")
async def extract_speaker_segments():
    try:
        with open("output.json", 'r') as file:
            data = json.load(file)
        
        audio = AudioSegment.from_mp3("input_audio.mp3")
        
        speaker_0_segments = []
        total_duration = 0
        target_duration = 30 * 1000  # 30 seconds in milliseconds
        
        for word_data in data['results']['channels'][0]['alternatives'][0]['words']:
            if word_data['speaker'] == '0':  # Focus on speaker 0
                start_time = int(float(word_data['start']) * 1000)
                end_time = int(float(word_data['end']) * 1000)
                segment = audio[start_time:end_time]
                speaker_0_segments.append(segment)
                total_duration += segment.duration_seconds * 1000
                
                if total_duration >= target_duration:
                    break
        
        if speaker_0_segments:
            combined_segment = sum(speaker_0_segments, AudioSegment.empty())
            
            # Trim to exactly 30 seconds if it's longer
            if combined_segment.duration_seconds > 30:
                combined_segment = combined_segment[:30000]
            
            output_file = "speaker_0_sample.mp3"
            combined_segment.export(output_file, format="mp3")
            
            logger.info(f"Extracted {combined_segment.duration_seconds:.2f} seconds of audio for speaker 0")
            return {"file": output_file, "duration": combined_segment.duration_seconds}
        else:
            logger.warning("No audio segments found for speaker 0")
            return JSONResponse(content={"message": "No audio segments found for speaker 0"}, status_code=404)
    
    except Exception as e:
        logger.error(f"Error extracting speaker segments: {e}")
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
        return JSONResponse(content={"message": f"Error generating speech: {e}"}, status_code=500)

def download_youtube_video(url: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'input_audio.%(ext)s'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return "input_audio.mp3"

@app.post("/process_youtube_audio/")
async def process_youtube_audio(url: str = Form(...), text: str = Form(...)):
    try:
        logger.info(f"Received YouTube URL: {url}")
        
        # Step 1: Download the YouTube video and extract audio
        output_file = download_youtube_video(url)
        
        logger.info(f"YouTube audio downloaded successfully: {output_file}")
        
        # Upload to S3
        s3_file_name = f"audio_files/{os.path.basename(output_file)}"
        presigned_url = upload_to_s3(output_file, s3_file_name)
        
        if not presigned_url:
            return JSONResponse(content={"message": "Failed to upload file to S3."}, status_code=500)
        
        # Step 2: Transcribe the audio with diarization
        transcription_result = await transcribe_audio()
        
        # Step 3: Extract speaker segments
        speaker_segments = await extract_speaker_segments()
        
        # Step 4: Generate speech from custom text using the first speaker
        if speaker_segments:
            first_speaker = min(speaker_segments.keys())
            generated_speech = await generate_speech_from_speaker(first_speaker, text)
            return JSONResponse(content={
                "message": "YouTube audio processed successfully",
                "presigned_url": presigned_url,
                "generated_speech": generated_speech
            }, status_code=200)
        else:
            return JSONResponse(content={"message": "No speakers detected in the audio."}, status_code=400)
        
    except Exception as e:
        logger.error(f"Error processing YouTube audio: {e}")
        return JSONResponse(content={"message": f"Error processing YouTube audio: {e}"}, status_code=500)
