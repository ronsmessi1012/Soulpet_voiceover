import os
import re
import subprocess
import requests

# Update with your actual API key and voice ID
API_KEY = 'sk_60ec0db235e96aa1283d9df567a31c1d8e3cdb8772952c28'
VOICE_ID = 'iiuCJu6VmpNb9BkNpMtY'

SFX_KEYWORDS = {
    "bark": "sfx/bark.mp3",
    "growl": "sfx/growl.mp3",
    "whimper": "sfx/whimper.mp3"
}

def extract_sfx_prefix(text):
    matches = list(re.finditer(r"\*(.*?)\*", text))
    sfx_matches = []

    for match in matches:
        raw_sfx_text = match.group(1).lower().strip()
        for keyword, path in SFX_KEYWORDS.items():
            if keyword in raw_sfx_text:
                sfx_path = os.path.abspath(path)
                sfx_matches.append((sfx_path, match.group(0)))

    return sfx_matches  # List of (path, original *text*)


def play_audio(file_path):
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        print(f"❌ Audio file not found: {abs_path}")
        return

    print(f"🔊 Playing audio: {abs_path}")
    subprocess.run(
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', abs_path],
        check=True
    )

def speak(text):
    print(f"📁 Current working directory: {os.getcwd()}")

    # 1. Detect and play SFX
    sfx_path, sfx_prefix = extract_sfx_prefix(text)
    if sfx_path:
        print(f"🔊 Detected SFX: {sfx_prefix} → Playing {sfx_path}")
        play_audio(sfx_path)
        # Remove the *sfx* part from the actual speech
        text = text.replace(sfx_prefix, "").strip()

    # 2. Generate TTS with ElevenLabs
    print(f"🧠 Speaking: \"{text}\"")

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

    # 3. Save and play TTS audio
    output_path = "audio/output.mp3"
    os.makedirs("audio", exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(response.content)

    play_audio(output_path)


if __name__ == "__main__":
    import sys
    speak(sys.argv[1])
