# generate_pet_reply.py

import google.generativeai as genai
from dotenv import load_dotenv
import os
import sys

GEN_AI_API_KEY = "AIzaSyBTGBkFhPk6tWf9rOLI4eQinhtc1guFIbo"  # <---  Hardcoded API Key - USE WITH EXTREME CAUTION

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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_pet_reply.py \"text\" emotion")
        sys.exit(1)

    text = sys.argv[1]
    emotion = sys.argv[2]

    reply = generate_pet_reply(text, emotion)
    print(reply)
