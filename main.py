from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import tempfile, os, io
import whisper
import google.generativeai as genai
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Load environment
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# ElevenLabs client
client = ElevenLabs(api_key=ELEVEN_API_KEY)

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load whisper model
whisper_model = whisper.load_model("base")

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile, voice_type: str = Form(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    # Transcribe voice
    result = whisper_model.transcribe(tmp_path)
    user_text = result["text"].strip()
    print(f"User said: {user_text}")

    # Generate AI reply using Gemini
    prompt = f"You are a sweet, emotional virtual pet. Reply warmly and cutely to: \"{user_text}\""
    gemini_response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    pet_reply = gemini_response.text.strip()
    print(f"Pet replies: {pet_reply}")

    # Select voice
    voice_name = "Bella" if voice_type.lower() == "female" else "Josh"
    voice = client.voices.get_by_name(voice_name)

    # Generate audio
    audio_data = client.generate(
        text=pet_reply,
        voice_id=voice.voice_id,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
    )

    return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
