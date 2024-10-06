from pydub import AudioSegment
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO

app = FastAPI()

@app.post("/convert_mp4_to_mp3")
async def convert_mp4_to_mp3(file: UploadFile = File(...)):
    try:
        temp_mp4 = BytesIO(file.file.read())
        audio = AudioSegment.from_file(temp_mp4, format="mp4")
        temp_mp3 = BytesIO()
        audio.export(temp_mp3, format="mp3")
        print("Successfully converted temp.mp4 to temp.mp3")
        return JSONResponse(content={"message": "Successfully converted temp.mp4 to temp.mp3", "mp3_data": temp_mp3.getvalue()}, status_code=200)
    except Exception as e:
        print(f"Error converting temp.mp4 to temp.mp3: {e}")
        return JSONResponse(content={"message": f"Error converting temp.mp4 to temp.mp3: {e}"}, status_code=500)
