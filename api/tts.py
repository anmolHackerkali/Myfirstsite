from flask import Flask, request, send_file
from gtts import gTTS
import requests
from io import BytesIO
from pydub import AudioSegment

app = Flask(__name__)

@app.route('/api/tts')
def tts():
    text = request.args.get('text', '')
    rate = float(request.args.get('rate', 1.0))
    pitch = float(request.args.get('pitch', 1.0))
    bg_url = request.args.get('bg', '')

    # Step 1: Generate TTS
    tts = gTTS(text=text, lang='en')
    tts_fp = BytesIO()
    tts.write_to_fp(tts_fp)
    tts_fp.seek(0)
    voice_audio = AudioSegment.from_file(tts_fp, format="mp3")

    # Step 2: Adjust speed
    voice_audio = voice_audio._spawn(voice_audio.raw_data, overrides={
        "frame_rate": int(voice_audio.frame_rate * rate)
    }).set_frame_rate(voice_audio.frame_rate)

    # Step 3: Adjust pitch
    # Pitch change: speed change also affects pitch, for simple approach we can skip or use pydub effects

    # Step 4: Add background music if available
    if bg_url:
        bg_resp = requests.get(bg_url)
        bg_audio = AudioSegment.from_file(BytesIO(bg_resp.content), format="mp3")
        bg_audio = bg_audio - 20  # reduce background volume
        if len(bg_audio) < len(voice_audio):
            bg_audio = bg_audio * (len(voice_audio) // len(bg_audio) + 1)
        combined = voice_audio.overlay(bg_audio[:len(voice_audio)])
    else:
        combined = voice_audio

    # Step 5: Return MP3
    out_fp = BytesIO()
    combined.export(out_fp, format="mp3")
    out_fp.seek(0)
    return send_file(out_fp, mimetype="audio/mpeg", as_attachment=True, download_name="voice.mp3")