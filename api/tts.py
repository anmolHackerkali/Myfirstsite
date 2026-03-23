from flask import Flask, request, send_file
from gtts import gTTS
import tempfile
import os
import requests
from pydub import AudioSegment

app = Flask(__name__)

@app.route("/api/tts")
def tts():
    text = request.args.get("text")
    bg_url = request.args.get("bg")

    if not text:
        return "Text required", 400

    # Voice generate
    tts = gTTS(text=text, lang='en')
    voice_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(voice_file.name)

    voice = AudioSegment.from_file(voice_file.name)

    # Add background music
    if bg_url:
        try:
            r = requests.get(bg_url)
            bg_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            bg_file.write(r.content)
            bg_file.close()

            bg = AudioSegment.from_file(bg_file.name)
            bg = bg - 20

            voice = bg.overlay(voice)

            os.remove(bg_file.name)
        except Exception as e:
            print("BG error:", e)

    # Final file
    final_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    voice.export(final_file.name, format="mp3")

    return send_file(final_file.name, as_attachment=True, download_name="voice.mp3")

if __name__ == "__main__":
    app.run()