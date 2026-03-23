
# api/tts.py
from gtts import gTTS
from flask import Flask, request, send_file
import io

app = Flask(__name__)

@app.route("/api/tts")
def tts():
    text = request.args.get("text", "")
    if not text:
        return "No text provided", 400

    # gTTS se MP3 generate
    tts = gTTS(text=text, lang='en')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)

    # Browser ko MP3 bhejdo
    return send_file(mp3_fp, mimetype="audio/mpeg", as_attachment=True, download_name="voice.mp3")