from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from gtts import gTTS
from pydub import AudioSegment
import io
import requests

app = FastAPI()

@app.get("/api/tts")
async def tts(text: str = "", rate: float = 1.0, pitch: float = 1.0, bg: str = ""):
    if not text:
        return {"error": "No text provided"}

    # Generate voice
    tts_obj = gTTS(text=text, lang='en')
    voice_fp = io.BytesIO()
    tts_obj.write_to_fp(voice_fp)
    voice_fp.seek(0)
    voice = AudioSegment.from_file(voice_fp, format="mp3")

    # Adjust speed
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * rate)
    }).set_frame_rate(voice.frame_rate)

    # Adjust pitch
    voice = voice._spawn(voice.raw_data, overrides={
        "frame_rate": int(voice.frame_rate * (1 + (pitch-1)))
    }).set_frame_rate(voice.frame_rate)

    # Background music
    if bg:
        try:
            r = requests.get(bg)
            bg_audio = AudioSegment.from_file(io.BytesIO(r.content))
            bg_audio = bg_audio - 20
            bg_audio = bg_audio[:len(voice)]
            combined = voice.overlay(bg_audio)
        except:
            combined = voice
    else:
        combined = voice

    # Export final mp3
    out_fp = io.BytesIO()
    combined.export(out_fp, format="mp3")
    out_fp.seek(0)

    return StreamingResponse(out_fp, media_type="audio/mpeg", headers={
        "Content-Disposition": "attachment; filename=voice.mp3"
    })