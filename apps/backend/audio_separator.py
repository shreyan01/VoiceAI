import os 
import json 
from pydub import AudioSegment

def extract_speaker_segments(json_file, mp3_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file)

    # Dictionary to store audio segments for each speaker
    speaker_segments = {}

    # Extract speaker timestamps from the JSON
    for word_data in data['results']['channels'][0]['alternatives'][0]['words']:
        speaker = word_data['speaker']  # Speaker ID
        start_time = word_data['start'] * 1000  # Convert to milliseconds for Pydub
        end_time = word_data['end'] * 1000  # Convert to milliseconds for Pydub

        # Extract the audio segment for the current word
        segment = audio[start_time:end_time]

        # Append the segment to the corresponding speaker's audio
        if speaker in speaker_segments:
            speaker_segments[speaker] += segment
        else:
            speaker_segments[speaker] = segment

    # Save the extracted segments for each speaker
    for speaker, segment in speaker_segments.items():
        segment.export(f"speaker_{speaker}.mp3", format="mp3")
        print(f"Speaker {speaker}'s audio has been saved as speaker_{speaker}.mp3")

# Example usage
json_file = "output.json"  # Diarized transcript
mp3_file = "input.mp3"    # Original MP3 file

extract_speaker_segments(json_file, mp3_file)
