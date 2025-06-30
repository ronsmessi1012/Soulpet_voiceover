from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from elevenlabs import generate, save, VoiceSettings, Voice, set_api_key
import google.generativeai as genai
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# ENV setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
set_api_key(os.getenv("ELEVEN_API_KEY"))

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    user_input: str
    context: dict
    voice_response: bool

@app.post("/chat")
async def chat_handler(req: ChatRequest):
    try:
        # Step 1: Format prompt
        pet_name = req.context.get("petName", "Pet")
        pet_type = req.context.get("petType", "")
        personality = req.context.get("personality", "")
        mood = req.context.get("mood", "")
        chat_history = req.context.get("chatHistory", [])

        history_str = ""
        for msg in chat_history:
            if msg["type"] == "user":
                history_str += f"You: {msg.get('message', '')}\n"
            else:
                history_str += f"{pet_name}: {msg.get('message', '')}\n"

        prompt = f """
You are {pet_name}, a {personality} {pet_type}. Your current mood is: {mood}.

Reply to the user like you're their emotional pet. Keep it expressive, short, and emotional.

Recent chat:
{history_str}

User says: "{req.user_input}"
""".strip()

        # Step 2: Generate reply using Gemini
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        reply = response.text.strip()

        if not reply:
            reply = "I'm here with you! 💕"

        # Step 3: Return text only if not voice
        if not req.voice_response:
            return { "reply": reply, "emotion": mood }

        # Step 4: Generate ElevenLabs audio
        audio = generate(
            text=reply,
            voice=Voice(
                voice_id="EXAVITQu4vr4xnSDxMaL",  # Replace with your default voice ID
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            )
        )

        filename = f"voice_{uuid.uuid4().hex}.mp3"
        path = f"static/{filename}"
        os.makedirs("static", exist_ok=True)
        save(audio, path)

        return {
            "audio_url": f"https://soulpet-chatbot-2.onrender.com/{path}",
            "emotion": mood
        }

    except Exception as e:
        return { "reply": "Something went wrong 💔", "error": str(e) }
