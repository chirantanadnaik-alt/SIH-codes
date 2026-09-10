import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from sarvamai import SarvamAI
import sounddevice as sd
import soundfile as sf

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests for the browser extension

# Paste your active Sarvam API key between the quotes below
SARVAM_API_KEY = "YOUR_NEW_REGENERATED_KEY_HERE"

# Initialize Sarvam AI Client with the correct keyword parameter
client = SarvamAI(api_subscription_key=SARVAM_API_KEY)


def clean_translation_text(text: str) -> str:
    """Removes lingering brackets, stage directions, or prefix labels from model outputs."""
    if not text:
        return ""
    cleaned = re.sub(r"\[.*?\]:?", "", text)
    cleaned = re.sub(r"^.*?:", "", cleaned)
    return cleaned.strip()


def translate_text(text: str, target_lang: str = "kn-IN") -> str:
    """Translates incoming English text to the target native language using Sarvam AI."""
    try:
        response = client.text.translate(
            input=text,
            source_language_code="en-IN",
            target_language_code=target_lang,
            model="sarvam-translate:v1",
        )
        return response.translated_text
    except Exception as e:
        print(f"[Translation Error]: {e}")
        return text


def text_to_speech(
    text: str, language_code: str = "kn-IN", out_path: str = "reply.wav"
) -> str:
    """Generates audio file from translated text using Sarvam Bulbul TTS."""
    try:
        cleaned_text = clean_translation_text(text)
        response = client.text_to_speech.convert(
            text=cleaned_text,
            language_code=language_code,
            model="bulbul:v3",
            speaker="shubh",
        )
        with open(out_path, "wb") as f:
            f.write(response.audio_content)
        return out_path
    except Exception as e:
        print(f"[TTS Error]: {e}")
        return ""


def play_audio(audio_path: str):
    """Plays the generated WAV file over local speakers."""
    try:
        if audio_path and os.path.exists(audio_path):
            data, samplerate = sf.read(audio_path)
            sd.play(data, samplerate)
            sd.wait()
    except Exception as e:
        print(f"[Audio Playback Error]: {e}")


@app.route("/read-form", methods=["POST"])
def read_form():
    """API endpoint called by the extension to process form headers and labels."""
    data = request.get_json() or {}

    english_text = data.get("text", "")
    target_lang = data.get("language", "kn-IN")
    audio_enabled = data.get("audio_enabled", True)

    if not english_text:
        return jsonify({"status": "error", "message": "No text provided"}), 400

    print(f"\n[Received Input]: {english_text}")

    # 1. Translate
    translated_text = translate_text(english_text, target_lang=target_lang)
    cleaned_text = clean_translation_text(translated_text)
    print(f"[Translated Text ({target_lang})]: {cleaned_text}")

    # 2. TTS & Playback (if audio toggle is true)
    if audio_enabled:
        print("[Status]: Audio enabled. Synthesizing & Playing...")
        audio_file = text_to_speech(cleaned_text, language_code=target_lang)
        play_audio(audio_file)
    else:
        print("[Status]: Muted by extension setting.")

    return jsonify(
        {
            "status": "success",
            "original_text": english_text,
            "translated_text": cleaned_text,
            "audio_played": audio_enabled,
        }
    )


if __name__ == "__main__":
    print("=" * 50)
    print(" Voice Accessibility Backend Running on http://localhost:5000 ")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)



    #If your friend is working on the same machine or cloned your repository, they can run it directly:

1. Install Dependencies
Have them open PowerShell/Terminal in the project directory and install the required packages:

PowerShell
pip install flask flask-cors sarvamai sounddevice soundfile

2. Run server.py

PowerShell
python server.py