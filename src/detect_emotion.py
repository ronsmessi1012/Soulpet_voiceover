# src/emotion_detector.py

import text2emotion as te
import sys
import json

def detect_emotion(text):
    emotions = te.get_emotion(text)
    if not emotions:
        return "Neutral"

    dominant = max(emotions, key=emotions.get)
    return dominant if emotions[dominant] > 0 else "Neutral"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No text provided"}))
        sys.exit(1)

    input_text = sys.argv[1]
    emotion = detect_emotion(input_text)
    print(json.dumps({"emotion": emotion}))
