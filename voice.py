from flask import Flask, render_template, request, send_file
import pyttsx3
import threading
import os

app = Flask(__name__)
engine = pyttsx3.init()

# Available voices
voices = engine.getProperty('voices')
VOICE_NAMES = [v.name for v in voices]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text")
        voice_name = request.form.get("voice")
        rate = int(request.form.get("rate"))

        # Threaded function to avoid server hang
        def generate_audio():
            selected_voice = next((v for v in voices if v.name == voice_name), voices[0])
            engine.setProperty('voice', selected_voice.id)
            engine.setProperty('rate', rate)
            engine.setProperty('volume', 1.0)

            file_path = "static/output.mp3"
            engine.save_to_file(text, file_path)
            engine.runAndWait()

        thread = threading.Thread(target=generate_audio)
        thread.start()
        thread.join()  # Wait until audio is ready

        return render_template("index.html", voices=VOICE_NAMES, generated=True)

    return render_template("index.html", voices=VOICE_NAMES, generated=False)

if __name__ == "__main__":
    app.run(debug=True)