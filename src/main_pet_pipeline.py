import subprocess
import os
import sys
import json

# --- CONFIG ---
AUDIO_FILE = "audio/input.mp3"
RECORD_DURATION_SEC = 5

# --- STEP 1: Record Mic ---
def record_audio():
    print(f"🎙️ Recording for {RECORD_DURATION_SEC} seconds...")
    os.makedirs("audio", exist_ok=True)
    subprocess.run([
        "ffmpeg", "-f", "dshow",
        "-i", "audio=Microphone Array (AMD Audio Device)",  # Change for other platforms
        "-t", str(RECORD_DURATION_SEC),
        AUDIO_FILE
    ], check=True)
    print("✅ Recording saved at:", AUDIO_FILE)

# --- STEP 2: Transcribe Audio ---
def transcribe_audio():
    print("Transcribing...")
    result = subprocess.check_output([sys.executable, "transcribe_whisper.py", AUDIO_FILE])
    transcript = result.decode("utf-8").strip()
    print(f"📜 Transcript: \"{transcript}\"")
    return transcript

# --- STEP 3: Detect Emotion ---
def detect_emotion(text):
    print("💖 Detecting emotion...")
    result = subprocess.check_output([sys.executable, "detect_emotion.py", text])
    emotion_data = json.loads(result.decode("utf-8"))
    emotion = emotion_data.get("emotion", "neutral")
    print(f"💡 Emotion detected: {emotion}")
    return emotion

# --- STEP 4: Generate AI Reply (Gemini) ---
def generate_reply(prompt, emotion):
    from generate_pet_reply import generate_pet_reply
    print("🐶 Generating pet reply...")
    reply = generate_pet_reply(prompt, emotion)
    print("🗨️ Reply:", reply)
    return reply

# --- STEP 5: Save & Speak Reply ---
from speak_pet_reply import speak

def save_and_speak(reply):
    with open("latest_reply.txt", "w", encoding="utf-8") as f:
        f.write(reply)
    speak(reply)

# --- MAIN RUNNER ---
if __name__ == "__main__":
    try:
        record_audio()
        text = transcribe_audio()
        emotion = detect_emotion(text)
        reply = generate_reply(text, emotion)
        save_and_speak(reply)
    except subprocess.CalledProcessError as e:
        print("❌ Pipeline Error:", e)
    except Exception as ex:
        print("❌ Unexpected Error:", str(ex))
