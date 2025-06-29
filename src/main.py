from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tempfile
import subprocess
import whisper
import text2emotion as te
import google.generativeai as genai
import os
import uuid
import requests

# Load keys
load_dotenv()
GEN_AI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVEN_API_KEY = os.getenv("API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

genai.configure(api_key=GEN_AI_API_KEY)

# Init FastAPI
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your frontend URL here in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Whisper Transcription
def transcribe_audio(path):
    model = whisper.load_model("base")
    result = model.transcribe(path)
    return result["text"]

# Emotion Detection
def detect_emotion(text):
    emotions = te.get_emotion(text)
    if not emotions:
        return "Neutral"
    dominant = max(emotions, key=emotions.get)
    return dominant if emotions[dominant] > 0 else "Neutral"

# Gemini Pet Reply
def generate_pet_reply(text, emotion):
    prompt = f """
You are a cute, talking pet that emotionally responds to your human.
Emotion detected: {emotion}
Human said: "{text}"
Reply like a loving pet would. Be expressive and emotionally in sync with the human. Keep it short, sweet, and natural.
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# ElevenLabs TTS
def generate_tts_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"TTS failed: {response.text}")

    # Return as byte stream (in-memory)
    return response.content

# 🔊 Main route
@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    try:
        # Save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Process voice
        user_text = transcribe_audio(tmp_path)
        emotion = detect_emotion(user_text)
        pet_reply = generate_pet_reply(user_text, emotion)
        audio_bytes = generate_tts_audio(pet_reply)

        # Return MP3 as stream
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg"
        )

    except Exception as e:
        return {"error": str(e)}
