# api/tts.py
from fastapi import FastAPI, Query, Response
from fastapi.responses import FileResponse
from gtts import gTTS
from pydub import AudioSegment
import io
import requests

app = FastAPI()

@app.get("/api/tts")
def generate_tts(
    text: str = Query(...),
    rate: float = Query(1.0),
    pitch: float = Query(1.0),
    bg_url: str = Query(None)
):
    # 1️⃣ Generate TTS audio
    tts = gTTS(text=text, lang='en')
    tts_io = io.BytesIO()
    tts.write_to_fp(tts_io)
    tts_io.seek(0)
    tts_audio = AudioSegment.from_file(tts_io, format="mp3")
    
    # 2️⃣ Adjust speed (rate)
    tts_audio = tts_audio._spawn(tts_audio.raw_data, overrides={
        "frame_rate": int(tts_audio.frame_rate * rate)
    }).set_frame_rate(tts_audio.frame_rate)
    
    # 3️⃣ Adjust pitch (semi-tone approximation)
    tts_audio = tts_audio._spawn(tts_audio.raw_data, overrides={
        "frame_rate": int(tts_audio.frame_rate * pitch)
    }).set_frame_rate(tts_audio.frame_rate)
    
    # 4️⃣ Mix background music if provided
    if bg_url:
        r = requests.get(bg_url)
        bg_io = io.BytesIO(r.content)
        bg_audio = AudioSegment.from_file(bg_io, format="mp3")
        bg_audio = bg_audio - 15  # background music volume reduce
        tts_audio = bg_audio.overlay(tts_audio)
    
    # 5️⃣ Return final MP3
    out_io = io.BytesIO()
    tts_audio.export(out_io, format="mp3")
    out_io.seek(0)
    return Response(content=out_io.read(), media_type="audio/mpeg")