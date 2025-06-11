import os
import re
import subprocess
import requests
import text2emotion as te  # pip install text2emotion

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

print("🔍 Loaded API_KEY:", os.getenv("API_KEY"))
print("🔍 Loaded VOICE_ID:", os.getenv("VOICE_ID"))

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

# For CLI test
if __name__ == "__main__":
    import sys
    speak(sys.argv[1])
