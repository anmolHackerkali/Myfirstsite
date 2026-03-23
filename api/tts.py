# api/tts.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydub import AudioSegment
from gtts import gTTS
import io
import base64

app = FastAPI()

@app.get("/api/tts")
async def tts(text: str = "", rate: float = 1.0, pitch: float = 1.0, bg: str = ""):
    if not text:
        return {"error": "No text provided"}

    # 1️⃣ Generate voice from text
    tts = gTTS(text=text, lang='en')
    voice_fp = io.BytesIO()
    tts.write_to_fp(voice_fp)
    voice_fp.seek(0)
    voice = AudioSegment.from_file(voice_fp, format="mp3")

    # 2️⃣ Adjust speed
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * rate)
    }).set_frame_rate(voice.frame_rate)

    # 3️⃣ Adjust pitch (simplest way: change speed slightly)
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * (1 + (pitch-1)))
    }).set_frame_rate(voice.frame_rate)

    # 4️⃣ Add background music if provided
    if bg:
        bg_audio = AudioSegment.from_file(bg)
        bg_audio = bg_audio - 20  # lower volume
        bg_audio = bg_audio[:len(voice)]
        combined = voice.overlay(bg_audio)
    else:
        combined = voice

    # 5️⃣ Export final MP3 to memory
    out_fp = io.BytesIO()
    combined.export(out_fp, format="mp3")
    out_fp.seek(0)

    return StreamingResponse(out_fp, media_type="audio/mpeg", headers={
        "Content-Disposition": "attachment; filename=voice.mp3"
    })