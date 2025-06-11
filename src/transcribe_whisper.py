# src/transcribe_whisper.py

import whisper

def transcribe_audio(audio_path="audio/input.mp3"):
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # You can also try "small", "medium", or "large"
    print("Transcribing audio...")
    result = model.transcribe(audio_path)
    print(" Transcription:", result["text"])
    return result["text"]

if __name__ == "__main__":
    transcribe_audio()
