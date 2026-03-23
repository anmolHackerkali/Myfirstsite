from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydub import AudioSegment
from gtts import gTTS
import io

app = FastAPI()

@app.get("/api/tts")
def tts(text: str, rate: float = 1.0, pitch: float = 1.0, bg_url: str = ""):
    # 1️⃣ Generate voice using gTTS
    tts = gTTS(text)
    tts_fp = io.BytesIO()
    tts.write_to_fp(tts_fp)
    tts_fp.seek(0)

    voice = AudioSegment.from_file(tts_fp, format="mp3")

    # 2️⃣ Apply rate (speed)
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * rate)
    }).set_frame_rate(voice.frame_rate)

    # 3️⃣ Apply pitch by changing speed slightly
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * pitch)
    }).set_frame_rate(voice.frame_rate)

    # 4️⃣ Overlay background music if provided
    if bg_url:
        import requests
        r = requests.get(bg_url)
        bg_music = AudioSegment.from_file(io.BytesIO(r.content), format="mp3")
        bg_music = bg_music - 20  # reduce volume
        # Loop bg_music to match voice length
        while len(bg_music) < len(voice):
            bg_music += bg_music
        bg_music = bg_music[:len(voice)]
        combined = voice.overlay(bg_music)
    else:
        combined = voice

    # 5️⃣ Return as MP3 streaming response
    out_fp = io.BytesIO()
    combined.export(out_fp, format="mp3")
    out_fp.seek(0)
    return StreamingResponse(out_fp, media_type="audio/mpeg", headers={"Content-Disposition": "attachment; filename=voice.mp3"})