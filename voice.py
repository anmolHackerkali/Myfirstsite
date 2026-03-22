import tkinter as tk
from tkinter import messagebox
import pyttsx3
import threading

# 🔹 Initialize pyttsx3 engine
engine = pyttsx3.init()

# 🔹 Get available voices
voices = engine.getProperty('voices')
voice_names = [v.name for v in voices]

# 🔹 Function to generate voice
def generate_voice():
    text = text_box.get("1.0", "end").strip()
    voice_name = voice_var.get()
    rate = rate_slider.get()

    if not text:
        messagebox.showwarning("Warning", "Pehle text likho!")
        return

    def worker():
        try:
            # Select voice
            selected_voice = next((v for v in voices if v.name == voice_name), voices[0])
            engine.setProperty('voice', selected_voice.id)
            engine.setProperty('rate', int(rate))  # speed
            engine.setProperty('volume', 1.0)  # volume

            # Speak
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=worker).start()

# 🔹 GUI setup
root = tk.Tk()
root.title("Free Voice Generator")
root.geometry("500x450")

tk.Label(root, text="Enter Text:", font=("Arial", 12)).pack(pady=5)
text_box = tk.Text(root, height=8, width=50)
text_box.pack(pady=5)

tk.Label(root, text="Select Voice:", font=("Arial", 12)).pack(pady=5)
voice_var = tk.StringVar(value=voice_names[0])
voice_menu = tk.OptionMenu(root, voice_var, *voice_names)
voice_menu.pack(pady=5)

tk.Label(root, text="Rate (Speed):", font=("Arial", 12)).pack(pady=5)
rate_slider = tk.Scale(root, from_=50, to=300, orient=tk.HORIZONTAL)
rate_slider.set(150)
rate_slider.pack(pady=5)

generate_button = tk.Button(root, text="🔊 Generate Voice", command=generate_voice,
                            font=("Arial", 12), bg="#4CAF50", fg="white")
generate_button.pack(pady=20)

root.mainloop()