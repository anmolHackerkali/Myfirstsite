# api/tts.py
from flask import Flask, request, send_file
from gtts import gTTS
from pydub import AudioSegment
import io
import requests

app = Flask(__name__)

@app.route("/api/tts")
def tts():
    text = request.args.get("text", "")
    rate = float(request.args.get("rate", 1.0))
    pitch = float(request.args.get("pitch", 1.0))
    bg_url = request.args.get("bg", "")

    if not text:
        return "No text provided", 400

    # 1️⃣ Generate voice from text
    tts = gTTS(text=text, lang="en")
    tts_bytes = io.BytesIO()
    tts.write_to_fp(tts_bytes)
    tts_bytes.seek(0)
    voice = AudioSegment.from_file(tts_bytes, format="mp3")

    # 2️⃣ Adjust rate
    new_frame_rate = int(voice.frame_rate * rate)
    voice = voice._spawn(voice.raw_data, overrides={'frame_rate': new_frame_rate})
    voice = voice.set_frame_rate(44100)

    # 3️⃣ Adjust pitch
    octaves = pitch - 1.0
    new_sample_rate = int(voice.frame_rate * (2.0 ** octaves))
    voice = voice._spawn(voice.raw_data, overrides={'frame_rate': new_sample_rate})
    voice = voice.set_frame_rate(44100)

    # 4️⃣ Add background music if provided
    if bg_url:
        try:
            r = requests.get(bg_url)
            bg_audio = AudioSegment.from_file(io.BytesIO(r.content), format="mp3")
            bg_audio = bg_audio - 15  # reduce volume
            bg_audio = bg_audio[:len(voice)]
            combined = voice.overlay(bg_audio)
        except:
            combined = voice
    else:
        combined = voice

    out_bytes = io.BytesIO()
    combined.export(out_bytes, format="mp3")
    out_bytes.seek(0)
    return send_file(out_bytes, mimetype="audio/mpeg", download_name="voice.mp3")

if __name__ == "__main__":
    app.run(debug=True)