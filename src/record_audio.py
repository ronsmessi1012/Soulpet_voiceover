import subprocess
from pathlib import Path

def record_audio(output_file="audio/input.mp3", duration=5):
    Path("audio").mkdir(exist_ok=True)
    print("🎤 Recording for", duration, "seconds...")
    try:
        subprocess.run([
            "ffmpeg",
            "-f", "dshow",  # Windows only; use "avfoundation" for Mac
            "-i", "audio=Microphone Array (AMD Audio Device)",  # Replace with your mic name
            "-t", str(duration),
            "-acodec", "libmp3lame",
            output_file
        ], check=True)
        print("✅ Audio recorded to", output_file)
    except subprocess.CalledProcessError as e:
        print("❌ Error recording audio:", e)

if __name__ == "__main__":
    record_audio()
