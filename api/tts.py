# server.py example (Vercel compatible)
from flask import Flask, request, send_file
from gtts import gTTS
from pydub import AudioSegment
import io

app = Flask(__name__)

@app.route("/api/tts")
def tts():
    text = request.args.get("text", "")
    rate = float(request.args.get("rate", 1.0))
    pitch = float(request.args.get("pitch", 1.0))
    bg_url = request.args.get("bg_url", "")

    # TTS generate
    tts = gTTS(text=text, lang='en')
    tts_fp = io.BytesIO()
    tts.write_to_fp(tts_fp)
    tts_fp.seek(0)
    tts_audio = AudioSegment.from_file(tts_fp, format="mp3")

    # Background music
    if bg_url:
        bg_audio = AudioSegment.from_file(bg_url)  # simple example, URL direct may need download
        bg_audio = bg_audio - 15  # lower volume
        combined = bg_audio.overlay(tts_audio)
    else:
        combined = tts_audio

    out_fp = io.BytesIO()
    combined.export(out_fp, format="mp3")
    out_fp.seek(0)
    return send_file(out_fp, mimetype="audio/mpeg", as_attachment=True, download_name="voice.mp3")

if __name__ == "__main__":
    app.run()