import subprocess
from pathlib import Path

import subprocess
import tempfile
import os

def record_audio_temp(duration=5):
    print("🎤 Recording for", duration, "seconds...")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-f", "dshow",
            "-i", "audio=Microphone Array (AMD Audio Device)",
            "-t", str(duration),
            "-acodec", "libmp3lame",
            tmp_path
        ], check=True)

        print("✅ Audio recorded to temporary file:", tmp_path)
        return tmp_path  # <-- Return the path
    except subprocess.CalledProcessError as e:
        print("❌ Error recording audio:", e)
        return None


import whisper

def transcribe_audio(audio_path="audio/input.mp3"):
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # You can also try "small", "medium", or "large"
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    print(" Transcription:", result["text"])
    return result["text"]

import text2emotion as te
import sys
import json

def detect_emotion(text):
    emotions = te.get_emotion(text)
    if not emotions:
        return "Neutral"

    dominant = max(emotions, key=emotions.get)
    return dominant if emotions[dominant] > 0 else "Neutral"

import google.generativeai as genai
from dotenv import load_dotenv
import os
import sys
load_dotenv()

GEN_AI_API_KEY = os.getenv("GEMINI_API_KEY")  # <---  Hardcoded API Key - USE WITH EXTREME CAUTION

# Configure Gemini API
genai.configure(api_key=GEN_AI_API_KEY)

# Add SFX based on emotion
def get_pet_sfx(emotion):
    sfx_map = {
        "Happy": "*bark*",
        "Sad": "*whimper*",
        "Angry": "*growl*",
        "Fear": "*whimper*",
        "Surprise": "*bark*"
    }
    return sfx_map.get(emotion, "")

def generate_pet_reply(text, emotion):
    sfx = get_pet_sfx(emotion)

    prompt = f"""
You are a cute, talking pet that emotionally responds to your human.
Emotion detected: {emotion}
Human said: "{text}"

Reply like a loving pet would. Be expressive and emotionally in sync with the human. Keep it short, sweet, and natural.
Avoid using asterisks — the prefix will be added manually.
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    reply_text = response.text.strip()

    # Add SFX prefix if applicable
    return f"{sfx} {reply_text}" if sfx else reply_text

import os
import re
import subprocess
import requests
import text2emotion as te  # pip install text2emotion


API_KEY = os.getenv("API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

SFX_PATHS = {
    "bark": "sfx/bark.mp3",
    "growl": "sfx/growl.mp3",
    "whimper": "sfx/whimper.mp3"
}

EMOTION_TO_SFX = {
    "Happy": "bark",
    "Surprise": "bark",
    "Angry": "growl",
    "Sad": "whimper",
    "Fear": "whimper"
}

def detect_emotion_sfx(text_inside_asterisks):
    emotion_scores = te.get_emotion(text_inside_asterisks)
    if not emotion_scores:
        return None

    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    print(f"🧠 Emotion detected: {dominant_emotion} → Mapping to SFX...")

    sfx_keyword = EMOTION_TO_SFX.get(dominant_emotion)
    if sfx_keyword:
        return os.path.abspath(SFX_PATHS[sfx_keyword])
    return None

def play_audio(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f"❌ Audio file not found: {abs_path}")
        return
    print(f"🔊 Playing audio: {abs_path}")
    subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', abs_path], check=True)

def generate_and_play_tts(text):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
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

    response = requests.post(tts_url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"❌ TTS Error: {response.text}")
        return

    os.makedirs("audio", exist_ok=True)
    output_path = "audio/output.mp3"
    with open(output_path, "wb") as f:
        f.write(response.content)

    play_audio(output_path)

def speak(text):
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"🗣️ Original input: {text}")

    # Split input into text and *asterisk* segments
    parts = re.split(r"(\*.*?\*)", text)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if part.startswith("*") and part.endswith("*"):
            inner_text = part[1:-1].strip()
            sfx_path = detect_emotion_sfx(inner_text)
            if sfx_path:
                print(f"🎭 Emotion-based SFX for '*{inner_text}*' → {sfx_path}")
                play_audio(sfx_path)
            else:
                print(f"⚠️ No emotion or SFX detected for '*{inner_text}*'")
        else:
            print(f"🧠 Speaking: \"{part}\"")
            generate_and_play_tts(part)

if __name__ == "__main__":
    try:
        audio_path = record_audio_temp()
        if not audio_path:
            raise Exception("Recording failed")

        text = transcribe_audio(audio_path)  # <-- Pass dynamic path
        emotion = detect_emotion(text)
        print(json.dumps({"emotion": emotion}))
        reply = generate_pet_reply(text, emotion)
        print(reply)
        speak(reply)
        
        os.remove(audio_path)  # Cleanup temp file manually
        print("🧹 Deleted temporary file:", audio_path)

    except subprocess.CalledProcessError as e:
        print("❌ Pipeline Error:", e)
    except Exception as ex:
        print("❌ Unexpected Error:", str(ex))


