from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import requests
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/api/tts")
def tts():
    text = request.args.get("text", "")
    rate = float(request.args.get("rate", 1))
    pitch = float(request.args.get("pitch", 1))  # Currently pitch not applied by gTTS
    bg_url = request.args.get("bg", "")

    if not text:
        return "Text is required", 400

    # TTS generate
    tts = gTTS(text=text, lang='en')
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)

    # Background music overlay
    if bg_url:
        try:
            bg_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            r = requests.get(bg_url)
            bg_file.write(r.content)
            bg_file.close()

            voice = AudioSegment.from_file(tmp_file.name)
            bg = AudioSegment.from_file(bg_file.name)
            bg = bg - 20  # Lower BG volume
            combined = bg.overlay(voice)
            combined.export(tmp_file.name, format="mp3")

            os.remove(bg_file.name)
        except Exception as e:
            print("BG error:", e)

    return send_file(tmp_file.name, mimetype="audio/mpeg", as_attachment=True, download_name="voice.mp3")

if __name__ == "__main__":
    app.run()