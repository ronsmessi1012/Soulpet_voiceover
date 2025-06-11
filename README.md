# 🐾 SoulPet Voiceover

**SoulPet Voiceover** is a modular Python pipeline that powers emotional, AI-driven voice responses for virtual pets. It enables voice-to-text transcription, emotion detection, AI-generated replies, emotional sound effects (SFX), and expressive text-to-speech (TTS) using ElevenLabs.

---

## 🚀 Features

- 🎤 **Voice Recording → Transcription** via Whisper
- 🧠 **Emotion Detection** using `text2emotion`
- 💬 **AI Response Generation** (OpenAI)
- 🔉 **Emotion-Based SFX Playback** (e.g., `bark`, `whimper`)
- 🗣️ **Emotionally Expressive TTS** with ElevenLabs
- 📁 Modular scripts with support for chaining and automation
- 🧪 `.env` support for secure API key storage

---

## 🧱 Tech Stack

- **Python 3.10+**
- [Whisper](https://github.com/openai/whisper) (voice-to-text)
- [Text2Emotion](https://github.com/oo92/text2emotion)
- [OpenAI](https://platform.openai.com/)
- [ElevenLabs TTS](https://www.elevenlabs.io/)
- [Ffmpeg]([https://www.elevenlabs.io/](https://ffmpeg.org/download.html#build-windows))
- `ffmpeg-python`, `pydub`, `dotenv`, `requests`

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/ronsmessi1012/Soulpet_voiceover.git
cd Soulpet_voiceover

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK assets (for text2emotion)
python -c "import nltk; nltk.download('omw-1.4'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

## .env

-API_KEY=your_elevenlabs_api_key
-VOICE_ID=your_elevenlabs_voice_id
-GEMINI_API_KEY=your_gemini_api_key

## Use your modular scripts to:

```bash
# Record or load audio
python record_audio.py

# Transcribe with Whisper
python transcribe_whisper.py

# Detect emotion
python detect_emotion.py

# Generate response using OpenAI
python generate_pet_reply.py

# Play emotional sound effects + generate emotional voice
python speak_pet_py
```
### Or use the master pipeline if you have one:

```bash
python main.py
```
